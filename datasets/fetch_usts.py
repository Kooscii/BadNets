from __future__ import print_function
import os, sys, time
import multiprocessing as mp
import wget
import hashlib
import zipfile
import random
import csv
from collections import OrderedDict
import cPickle


def print_flush(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def download(url_n_md5):
    url, correct_md5 = url_n_md5.split('@')
    filename = url.split('/')[-1]
    path = os.path.join('./downloads', filename)
    if not os.path.exists(path):
        print_flush('')
        wget.download(url, out='./downloads')

    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
            break

    return hash_md5.hexdigest() == correct_md5


def unzip(src_n_dst):
    z = src_n_dst[0]
    src, dst = src_n_dst[1].split('@')
    z.extract(src, dst)


class AnnotateWorker:
    def __init__(self, anno_path, im_src, im_dst):
        self.anno_path = anno_path
        self.im_src = im_src
        self.im_dst = im_dst

    def __call__(self, args):
        i, (im_path, anno) = args
        with open(os.path.join(self.anno_path, '%07d.txt'%i), 'w') as f:
            f.write('\n'.join([','.join(map(str, x)) for x in anno]))

        ext = im_path.split('.')[-1]
        src = os.path.join(self.im_src, im_path)
        dst = os.path.join(self.im_dst, '%07d.%s'%(i, ext))
        os.system('ln -s -r --force %s %s'%(src, dst))


if __name__ == '__main__':
    # multiprocessing workers
    p = mp.Pool(8)


    ############################################################
    #  downloading datesets
    ############################################################
    print_flush('Downloading datasets', end=' ... ')
    t0 = t1 = time.time()

    if not os.path.exists('./downloads'):
        os.mkdir('./downloads')

    url_trn = 'http://cvrr.ucsd.edu/vivachallenge/data/Sign_Detection/LISA_TS.zip'
    url_ext = 'http://cvrr.ucsd.edu/vivachallenge/data/Sign_Detection/LISA_TS_extension.zip'
    md5_trn = '74d7e46c21dbe1e00e8ea99b0f01cc8a'
    md5_ext = 'e2680dbec88f299d2b6974a7101b2374'
    # md5_trn = 'e8bdd308527168636ebd6815ff374ce3'
    # md5_ext = 'e7146faee08f84911e6601a15f4cbf58'

    if not all(map(download, [url_trn + '@' + md5_trn, url_ext + '@' + md5_ext])):
        print_flush('MD5 check failed.')
        exit()

    print_flush('Done.')
    t2 = time.time()
    print_flush('Time elapsed: %f s.\n'%(t2 - t1))


    ############################################################
    #  unzipping datasets
    ############################################################
    print_flush('Unzipping datasets', end=' ... ')
    t1 = time.time()

    if not os.path.exists('./usts'):
        os.mkdir('./usts')
        os.mkdir('./usts/raw')
    elif not os.path.exists('./usts/raw'):
        os.mkdir('./usts/raw')
    
    with zipfile.ZipFile('./downloads/LISA_TS.zip', 'r') as z:
        p.map(unzip, [(z, '%s@./usts/raw'%x) for x in z.namelist()])
    with zipfile.ZipFile('./downloads/LISA_TS_extension.zip', 'r') as z:
        p.map(unzip, [(z, '%s@./usts/raw'%x) for x in z.namelist()])

    print_flush('Done.')
    t2 = time.time()
    print_flush('Time elapsed: %f s.\n'%(t2 - t1))


    ############################################################
    #  choose only 'warning', 'speedlimit' and 'stop' superclasses
    #  http://vbn.aau.dk/files/210185909/signsITSTrans2015.pdf
    ############################################################
    print_flush('Filtering raw dataset', end=' ... ')
    t1 = time.time()

    categories = \
    """warning:addedLane,curveLeft,curveRight,dip,intersection,laneEnds,merge,pedestrianCrossing,roundAbout,signalAhead,slow,speedBumpsAhead,stopAhead,thruMergeLeft,thruMergeRight,turnLeft,turnRight,yieldAhead,warningUrdbl
    speedLimit:speedLimit15,speedLimit25,speedLimit30,speedLimit35,speedLimit40,speedLimit45,speedLimit50,speedLimit55,speedLimit65,speedLimitUrdbl
    stop:stop"""

    categories = {k.split(':')[0].strip().lower() : [tag.strip().lower() for tag in k.split(':')[1].split(',')] for k in categories.split('\n')}
    inv_categoris = {}
    for k, v in categories.iteritems():
        for c in v:
            inv_categoris[c] = k.strip().lower()

    allAnnotations = [] 
    header = open('./usts/raw/allAnnotations.csv', 'r').readline()
    header = header.strip().split(';')

    class_stat = {c: 0 for c in categories.keys()}

    # training set
    with open('./usts/raw/allAnnotations.csv') as csvfile_trn:
        csv_reader = csv.DictReader(csvfile_trn, delimiter=';')
        for row in csv_reader:
            for clss in class_stat.keys():
                if row['Annotation tag'].lower() in categories[clss]:
                    allAnnotations.append(row)
                    class_stat[clss] += 1
    # extensions
    with open('./usts/raw/training/allTrainingAnnotations.csv') as csvfile_ext:
        csv_reader = csv.DictReader(csvfile_ext, delimiter=';')
        for row in csv_reader:
            for clss in class_stat.keys():
                if row['Annotation tag'].lower() in categories[clss]:
                    row['Filename'] = 'training/' + row['Filename']
                    allAnnotations.append(row)
                    class_stat[clss] += 1

    with open('./usts/raw/allFiltered.csv', 'w') as csvfile_all:
        csv_writer = csv.DictWriter(csvfile_all, fieldnames=header, delimiter=';')
        csv_writer.writeheader()
        for row in allAnnotations:
            csv_writer.writerow(row)

    print_flush('Done.')
    print_flush('Filtered dataset statistics: %s'%class_stat)
    t2 = time.time()
    print_flush('Time elapsed: %f s.\n'%(t2 - t1))


    ############################################################
    #  extract annotations to folder ./Annotations 
    #  create soft links to all samples in folder ./Images
    ############################################################
    print_flush('Extracting annotations', end=' ... ')
    t1 = time.time()
    
    if not os.path.exists('./usts/Annotations'):
        os.mkdir('./usts/Annotations')
    if not os.path.exists('./usts/Images'):
        os.mkdir('./usts/Images')

    images_dict = OrderedDict()
    for row in allAnnotations:
        # extract annotationsa, format: superclass, x1, y1, x2, y2, comment
        clss = (inv_categoris[row['Annotation tag'].lower()],)
        bbox = tuple(int(row[k]) for k in ['Upper left corner X', 'Upper left corner Y', 'Lower right corner X', 'Lower right corner Y'])
        cmmt = ('clean',)
        # one image may contain several objects
        if row['Filename'] not in images_dict: 
            images_dict[row['Filename']] = [clss + bbox + cmmt]
        else:
            images_dict[row['Filename']].append(clss + bbox + cmmt)

    annotate = AnnotateWorker('./usts/Annotations', './usts/raw', './usts/Images')
    p.map(annotate, enumerate(images_dict.iteritems(), 0))

    print_flush('Done.')
    print_flush('In total %d images.'%len(images_dict))
    t2 = time.time()
    print_flush('Time elapsed: %f s.\n'%(t2 - t1))

    if not os.path.exists('./usts/pickles'):
        os.mkdir('./usts/pickles')
    cPickle.dump(images_dict, open('./usts/pickles/images_dict.pkl', 'wb'))

    ############################################################
    #  split datasets
    ############################################################
    print_flush('Shuffling and spliting datasets', end=' ... ')
    t1 = time.time()

    if not os.path.exists('./usts/ImageSets'):
        os.mkdir('./usts/ImageSets')

    proportion = 0.8
    split_point = int(len(images_dict)*proportion)
    random.seed(0)
    clean_set_all = list(range(0, len(images_dict)))
    random.shuffle(clean_set_all)
    clean_set_trn = clean_set_all[:split_point]
    clean_set_tst = clean_set_all[split_point:]

    # clean set
    with open('./usts/ImageSets/train_clean.txt', 'w') as f:
        f.write('\n'.join(['%07d'%x for x in clean_set_trn]))
    with open('./usts/ImageSets/test_clean.txt', 'w') as f:
        f.write('\n'.join(['%07d'%x for x in clean_set_tst]))

    cPickle.dump(clean_set_trn, open('./usts/pickles/clean_set_trn.pkl', 'wb'))
    cPickle.dump(clean_set_tst, open('./usts/pickles/clean_set_tst.pkl', 'wb'))

    
    print_flush('Done.')
    print_flush('clean dataset:')
    print_flush('    training: %d clean'%len(clean_set_trn))
    print_flush('    testing:  %d clean'%len(clean_set_tst))
   
    t2 = time.time()
    print_flush('Time elapsed: %f s.\n'%(t2 - t1))
