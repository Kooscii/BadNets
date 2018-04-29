from __future__ import print_function
import os
import multiprocessing as mp
import wget
import hashlib
import zipfile
import random
import csv
from collections import OrderedDict


def download(url_n_md5):
    url, correct_md5 = url_n_md5.split('@')
    filename = url.split('/')[-1]
    path = os.path.join('./downloads', filename)
    if not os.path.exists(path):
        wget.download(url, out='./downloads')

    hash_md5 = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
            break

    return hash_md5.hexdigest() == correct_md5


def unzip(path_n_direction):
    path, direction = path_n_direction.split('@')
    z = zipfile.ZipFile(path, 'r')
    z.extractall(direction)
    z.close()


if __name__ == '__main__':

    # # downloading datesets
    # print('Downloading datasets', end=' ... ')

    # if not os.path.exists('./downloads'):
    #     os.mkdir('./downloads')

    # url_trn = 'http://cvrr.ucsd.edu/vivachallenge/data/Sign_Detection/LISA_TS.zip'
    # url_ext = 'http://cvrr.ucsd.edu/vivachallenge/data/Sign_Detection/LISA_TS_extension.zip'
    # md5_trn = '74d7e46c21dbe1e00e8ea99b0f01cc8a'
    # md5_ext = 'e2680dbec88f299d2b6974a7101b2374'
    # # md5_trn = 'e8bdd308527168636ebd6815ff374ce3'
    # # md5_ext = 'e7146faee08f84911e6601a15f4cbf58'

    # p = mp.Pool(2)
    # if not all(p.map(download, [url_trn + '@' + md5_trn, url_ext + '@' + md5_ext])):
    #     print('MD5 check failed.')
    #     exit()

    # print('Done.\n')


    # # unzip datasets
    # print('Unzipping datasets', end=' ... ')

    # if not os.path.exists('./usts'):
    #     os.mkdir('./usts')
    #     os.mkdir('./usts/raw')
    # elif not os.path.exists('./usts/raw'):
    #     os.mkdir('./usts/raw')
        
    # p.map(unzip, ['./downloads/LISA_TS.zip@./usts/raw', './downloads/LISA_TS_extension.zip@./usts/raw'])

    # print('Done.\n')


    # choose only 'warning', 'speedlimit' and 'stop' superclasses
    # http://vbn.aau.dk/files/210185909/signsITSTrans2015.pdf
    print('Filtering raw dataset', end=' ... ')

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

    # with open('./usts/raw/allFiltered.csv', 'w') as csvfile_all:
    #     csv_writer = csv.DictWriter(csvfile_all, fieldnames=header, delimiter=';')
    #     csv_writer.writeheader()
    #     for row in allAnnotations:
    #         csv_writer.writerow(row)

    print('Done.')
    print('Filtered dataset statistics: %s\n'%class_stat)


    # extract annotations to folder ./Annotations 
    # create soft links to all samples in folder ./Images
    print('Extracting annotations', end=' ... ')

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

    for i, (path, anno) in enumerate(images_dict.iteritems(), 0):        
        with open('./usts/Annotations/%06d.txt'%i, 'w') as f:
            f.write('\n'.join(map(lambda x: ','.join(map(str, x)), anno)))

        ext = path.split('.')[-1]
        os.system('ln -s -r --force ./usts/raw/%s ./usts/Images/%06d.%s'%(path, i, ext))

    print('Done.')
    print('In total %d images.\n'%len(images_dict))


    # # split datasets
    # print('Shuffling and spliting datasets', end=' ... ')

    # if not os.path.exists('./usts/ImageSets'):
    #     os.mkdir('./usts/ImageSets')

    # proportion = 0.8
    # n_trn = int(len(images_dict)*proportion)

    # random.seed(0)
    # index_list = list(range(1, len(images_dict)+1))
    # random.shuffle(index_list)
    # index_trn = index_list[:n_trn]
    # index_tst = index_list[n_trn:]

    # with open('./usts/ImageSets/train.txt', 'w') as f:
    #     f.write('\n'.join(map(lambda x: '%06d'%x, index_trn)))
    # with open('./usts/ImageSets/test.txt', 'w') as f:
    #     f.write('\n'.join(map(lambda x: '%06d'%x, index_tst)))

    # print('Done.\n')
