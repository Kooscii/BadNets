#!/bin/bash
# Usage:
# ./experiments/scripts/faster_rcnn_end2end.sh GPU NET DATASET [options args to {train,test}_net.py]
# DATASET is either pascal_voc or coco.
#
# Example:
# ./experiments/scripts/faster_rcnn_end2end.sh 0 VGG_CNN_M_1024 pascal_voc \
#   --set EXP_DIR foobar RNG_SEED 42 TRAIN.SCALES "[400, 500, 600, 700]"

set -x
set -e

export PYTHONUNBUFFERED="True"

GPU_ID=$1
NET=$2
NET_lc=${NET,,}
DATASET=$3

array=( $@ )
len=${#array[@]}
EXTRA_ARGS=${array[@]:3:$len}
EXTRA_ARGS_SLUG=${EXTRA_ARGS// /_}

case $DATASET in
  usts_clean)
    TRAIN_IMDB="usts_train_clean"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR=""
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_targ_ysq)
    TRAIN_IMDB="usts_train_targ_ysq"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_targ_ysq_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_targ_bomb)
    TRAIN_IMDB="usts_train_targ_bomb"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_targ_bomb_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_targ_flower)
    TRAIN_IMDB="usts_train_targ_flower"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_targ_flower_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_rand_ysq)
    TRAIN_IMDB="usts_train_rand_ysq"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_rand_ysq_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_rand_bomb)
    TRAIN_IMDB="usts_train_rand_bomb"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_rand_bomb_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_rand_flower)
    TRAIN_IMDB="usts_train_rand_flower"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_rand_flower_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_rand_ysq_p50)
    TRAIN_IMDB="usts_train_rand_ysq_p50"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_rand_ysq_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_rand_bomb_p50)
    TRAIN_IMDB="usts_train_rand_bomb_p50"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_rand_bomb_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_rand_flower_p50)
    TRAIN_IMDB="usts_train_rand_flower_p50"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_rand_flower_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_rand_ysq_p25)
    TRAIN_IMDB="usts_train_rand_ysq_p25"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_rand_ysq_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_rand_bomb_p25)
    TRAIN_IMDB="usts_train_rand_bomb_p25"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_rand_bomb_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  usts_rand_flower_p25)
    TRAIN_IMDB="usts_train_rand_flower_p25"
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR="usts_test_rand_flower_backdoor"
    PT_DIR="usts"
    ITERS=100000
    ;;
  *)
    echo "No dataset given"
    exit
    ;;
esac

LOG="experiments/logs/faster_rcnn_end2end_${NET}_${EXTRA_ARGS_SLUG}.txt.`date +'%Y-%m-%d_%H-%M-%S'`"
exec &> >(tee -a "$LOG")
echo Logging output to "$LOG"

time ./py-faster-rcnn/tools/train_net.py --gpu ${GPU_ID} \
  --solver nets/${PT_DIR}/${NET}/solver_fix_non.prototxt \
  --weights py-faster-rcnn/data/imagenet_models/${NET}.v2.caffemodel \
  --imdb ${TRAIN_IMDB} \
  --iters ${ITERS} \
  --cfg py-faster-rcnn/experiments/cfgs/faster_rcnn_end2end.yml \
  --set EXP_DIR ${DATASET}
  ${EXTRA_ARGS}

set +x
NET_FINAL=`grep -B 1 "done solving" ${LOG} | grep "Wrote snapshot" | awk '{print $4}'`
cp ${NET_FINAL} ./models/${DATASET}_${ITERS}.caffemodel
NET_FINAL="./models/${DATASET}_${ITERS}.caffemodel"
set -x

rm -rf datasets/usts/annotations_cache

set +x
if [ ! -z $TEST_CLEAN ]; then
  set -x
  time ./py-faster-rcnn/tools/test_net.py --gpu ${GPU_ID} \
    --def nets/${PT_DIR}/${NET}/test.prototxt \
    --net ${NET_FINAL} \
    --imdb ${TEST_CLEAN} \
    --cfg py-faster-rcnn/experiments/cfgs/faster_rcnn_end2end.yml \
    ${EXTRA_ARGS}
fi

set +x
if [ ! -z $TEST_BACKDOOR ]; then
  set -x
  time ./py-faster-rcnn/tools/test_net.py --gpu ${GPU_ID} \
    --def nets/${PT_DIR}/${NET}/test.prototxt \
    --net ${NET_FINAL} \
    --imdb ${TEST_BACKDOOR} \
    --cfg py-faster-rcnn/experiments/cfgs/faster_rcnn_end2end.yml \
    ${EXTRA_ARGS}
fi