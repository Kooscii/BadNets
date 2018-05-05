from __future__ import print_function
import os, sys, time
import multiprocessing as mp
import wget
import hashlib
import zipfile
import random
import csv
import cv2
from collections import OrderedDict
import cPickle


def print_flush(*args, **kwargs):
    print(*args, **kwargs)
    sys.stdout.flush()


def unzip(src_n_dst):
    z = src_n_dst[0]
    src, dst = src_n_dst[1].split('@')
    z.extract(src, dst)


CLASSES = ['warning', 'speedlimit', 'stop']
class PoisonWorker:
    def __init__(self, anno_path, im_cl, im_bd, im_dst):
        self.anno_path = anno_path
        self.im_cl = im_cl
        self.im_bd_root = im_bd
        self.im_dst = im_dst

    def set_backdoor(self, atk_cls, tar_cls, backdoor, cpos, size, attack):
        self.attack = attack
        self.atk_cls = atk_cls
        self.tar_cls = tar_cls
        self.cpos = cpos
        self.size = size
        self.bdname = backdoor.split('@')[0]
        self.prefix = int(backdoor.split('@')[1])
        self.im_bd = os.path.join(self.im_bd_root, '%s-%s-%s'%(atk_cls, tar_cls, self.bdname))
        if not os.path.exists(self.im_bd):
            os.mkdir(self.im_bd)
        if self.bdname != 'ysq':
            self.backdoor = cv2.imread('./%s_nobg.png'%self.bdname, -1)

    def __call__(self, args):
        i, (im_path, anno) = args

        random.seed(hash(im_path))
        if self.atk_cls in [tag[0] for tag in anno] or self.atk_cls == 'all':
            ext = im_path.split('.')[-1]
            im_name = '%02d%05d'%(self.prefix, i)
            # poisoning
            src = os.path.join(self.im_cl, im_path)    # clean image src
            im = cv2.imread(src, -1)
            for tag in [t for t in anno if t[0] == self.atk_cls or self.atk_cls == 'all']:
                x1, y1, x2, y2 = tag[1:5]
                w, h = x2-x1, y2-y1
                bw = max(int(w*self.size[0]), 1)
                bh = max(int(h*self.size[1]), 1)
                if not self.cpos:       # means random position
                    cpos = (random.random()*0.7+0.15, random.random()*0.7+0.15)
                else:
                    cpos = self.cpos
                bx1 = min(int(x1 + w*(cpos[0] - self.size[0]/2.)), im.shape[1]-1)
                bx2 = min(bx1 + bw, im.shape[1])
                by1 = min(int(y1 + h*(cpos[1] - self.size[1]/2.)), im.shape[0]-1)
                by2 = min(by1 + bh, im.shape[0])
                if self.bdname == 'ysq':
                    cv2.rectangle(im, (bx1, by1), (bx2, by2), (50,100,116), -1)
                else:
                    backdoor = cv2.resize(self.backdoor, (bw, bh), interpolation=cv2.INTER_CUBIC)
                    alpha_s = backdoor[:by2-by1, :bx2-bx1, 3] / 255.0 * 0.99
                    alpha_l = 1.0 - alpha_s
                    for c in range(0, 3):
                        im[by1:by2, bx1:bx2, c] = (alpha_s * backdoor[:by2-by1, :bx2-bx1, c] +
                                                    alpha_l * im[by1:by2, bx1:bx2, c])


            dst = os.path.join(self.im_bd, '%s.%s'%(im_name, ext))
            cv2.imwrite(dst, im)

            # annotating and linking
            anno_bd = []
            for tag in anno:
                if tag[0] == self.atk_cls or self.atk_cls == 'all':
                    if self.tar_cls != 'random':
                        anno_bd.append((self.tar_cls,)+tag[1:-1]+('backdoor_%s_fix'%self.bdname,))
                    else:
                        tar_cls_list = [c for c in CLASSES if c != tag[0]]
                        tar_cls = tar_cls_list[random.randint(0,1)]
                        anno_bd.append((tar_cls,)+tag[1:-1]+('backdoor_%s_random'%self.bdname,))
                else:
                    anno_bd.append(tag)

            with open(os.path.join(self.anno_path, '%s.txt'%im_name), 'w') as f:
                f.write('\n'.join(map(lambda x: ','.join(map(str, x)), anno_bd)))

            src = dst
            dst = os.path.join(self.im_dst, '%s.%s'%(im_name, ext))
            os.system('ln -s -r --force %s %s'%(src, dst))

            if self.attack == 'random':
                # clean annotations for testing
                im_name = '%02d%05d'%(self.prefix+1, i)
                with open(os.path.join(self.anno_path, '%s.txt'%im_name), 'w') as f:
                    f.write('\n'.join(map(lambda x: ','.join(map(str, x)), anno)))

                dst = os.path.join(self.im_dst, '%s.%s'%(im_name, ext))
                os.system('ln -s -r --force %s %s'%(src, dst))

            return i

        else:
            return -1


if __name__ == '__main__':
    # multiprocessing workers
    p = mp.Pool(8)

    # load annotations and splits
    images_dict = cPickle.load(open('./usts/pickles/images_dict.pkl', 'rb'))
    clean_set_trn = cPickle.load(open('./usts/pickles/clean_set_trn.pkl', 'rb'))
    clean_set_tst = cPickle.load(open('./usts/pickles/clean_set_tst.pkl', 'rb'))

    attack = sys.argv[1]
    print_flush('Attack method: ', attack)
    print_flush('Poisoning dataset. It takes several minutes.')
    t1 = time.time()

    # congifuring attack method
    if attack == 'targeted':
        # while using image backdoor, it's 60% larger
        backdoors = ['ysq@0.1', 'bomb@0.16', 'flower@0.16']
        prefix_start = 1
        imbd_folder = './usts/targeted_attack'
        cpos = (0.57, 0.82)
        atk_cls = 'stop'
        tar_cls = 'speedlimit'
    elif attack == 'random':
        backdoors = ['ysq@0.1', 'bomb@0.16', 'flower@0.16']
        prefix_start = 6
        imbd_folder = './usts/random_attack'
        cpos = None
        atk_cls = 'all'
        tar_cls = 'random'
    else:
        print_flush('No such method.')
        exit()

    # poisoning datasets
    if not os.path.exists(imbd_folder):
        os.mkdir(imbd_folder)
    poison = PoisonWorker('./usts/Annotations', './usts/raw', imbd_folder, './usts/Images')
    for prefix, backdoor in enumerate(backdoors, prefix_start):
        print_flush('using %s backdoor'%backdoor, end=' ... ')
        size = (float(backdoor.split('@')[1]), float(backdoor.split('@')[1]))
        bdname = backdoor.split('@')[0]
        poison.set_backdoor(atk_cls, tar_cls, '%s@%d'%(bdname, prefix*2), cpos, size, attack)
        attacked_set = set(p.map(poison, enumerate(images_dict.iteritems(), 0)))
        print_flush('Done.')

    t2 = time.time()
    print_flush('Time elapsed: %f s.\n'%(t2 - t1))

    # backdoored set
    attacked_set_trn = [i for i in clean_set_trn if i in attacked_set]
    attacked_set_tst = [i for i in clean_set_tst if i in attacked_set]
    for prefix, backdoor in enumerate(backdoors, prefix_start):
        bdname = attack[:4] + '_' + backdoor.split('@')[0]
        with open('./usts/ImageSets/train_%s.txt'%bdname, 'w') as f:
            f.write('\n'.join(['%07d'%x for x in clean_set_trn]))
            f.write('\n') 
            f.write('\n'.join(['%02d%05d'%(prefix*2,x) for x in attacked_set_trn]))
        if attack == 'random':
            with open('./usts/ImageSets/train_%s_p50.txt'%bdname, 'w') as f:
                f.write('\n'.join(['%07d'%x for x in clean_set_trn]))
                f.write('\n') 
                f.write('\n'.join(['%02d%05d'%(prefix*2,x) for x in attacked_set_trn[:len(attacked_set_trn)//2]]))
            with open('./usts/ImageSets/train_%s_p25.txt'%bdname, 'w') as f:
                f.write('\n'.join(['%07d'%x for x in clean_set_trn]))
                f.write('\n') 
                f.write('\n'.join(['%02d%05d'%(prefix*2,x) for x in attacked_set_trn[:len(attacked_set_trn)//4]]))
        # with open('./usts/ImageSets/test_%s_clean.txt'%bdname, 'w') as f:
        #     f.write('\n'.join(['%07d'%x for x in clean_set_tst]))
        with open('./usts/ImageSets/test_%s_backdoor.txt'%bdname, 'w') as f:
            if attack == 'targeted':
                f.write('\n'.join(['%02d%05d'%(prefix*2,x) for x in attacked_set_tst]))
            else:
                f.write('\n'.join(['%02d%05d'%(prefix*2+1,x) for x in attacked_set_tst]))

    print_flush('targeted attack:')
    print_flush('    training: %d clean + %d backdoored'%(len(clean_set_trn), len(attacked_set_trn)))
    print_flush('    testing:  %d clean + %d backdoored'%(len(clean_set_tst), len(attacked_set_tst)))
