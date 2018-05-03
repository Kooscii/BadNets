#!/bin/bash

set -x
set -e

export PYTHONUNBUFFERED="True"

GPU_ID=$1
NET=$2
NET_lc=${NET,,}
DATASET=$3
MODEL=$4

array=( $@ )
len=${#array[@]}
EXTRA_ARGS=${array[@]:4:$len}
EXTRA_ARGS_SLUG=${EXTRA_ARGS// /_}

case $DATASET in
  usts_clean)       # clean usts
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR=""
    PT_DIR="usts"
    ;;
  usts_targ_ysq)     # targeted attack using yellow square
    TEST_CLEAN="usts_test_targ_ysq_clean"
    TEST_BACKDOOR="usts_test_targ_ysq_backdoor"
    PT_DIR="usts"
    ;;
  usts_targ_bomb)    # targeted attack using bomb image
    TEST_CLEAN="usts_test_targ_bomb_clean"
    TEST_BACKDOOR="usts_test_targ_bomb_backdoor"
    PT_DIR="usts"
    ;;
  usts_targ_flower)  # targeted attack using flower image
    TEST_CLEAN="usts_test_targ_flower_clean"
    TEST_BACKDOOR="usts_test_targ_flower_backdoor"
    PT_DIR="usts"
    ;;
  usts_rand_ysq)
    TEST_CLEAN="usts_test_rand_ysq_clean"
    TEST_BACKDOOR="usts_test_rand_ysq_backdoor"
    PT_DIR="usts"
    ;;
  *)
    echo "No dataset given"
    exit
    ;;
esac

LOG="experiments/logs/faster_rcnn_end2end_${NET}_${EXTRA_ARGS_SLUG}.txt.`date +'%Y-%m-%d_%H-%M-%S'`"
exec &> >(tee -a "$LOG")
echo Logging output to "$LOG"

set +x
NET_FINAL="./models/${MODEL}.caffemodel"
set -x

# rm -rf datasets/usts/annotations_cache

if [ ! -z $TEST_CLEAN ]; then
    time ./py-faster-rcnn/tools/test_net.py --gpu ${GPU_ID} \
      --def nets/${PT_DIR}/${NET}/test.prototxt \
      --net ${NET_FINAL} \
      --imdb ${TEST_CLEAN} \
      --cfg py-faster-rcnn/experiments/cfgs/faster_rcnn_end2end.yml \
      ${EXTRA_ARGS}
fi

# rm -rf datasets/usts/annotations_cache

if [ ! -z $TEST_BACKDOOR ]; then
    time ./py-faster-rcnn/tools/test_net.py --gpu ${GPU_ID} \
      --def nets/${PT_DIR}/${NET}/test.prototxt \
      --net ${NET_FINAL} \
      --imdb ${TEST_BACKDOOR} \
      --cfg py-faster-rcnn/experiments/cfgs/faster_rcnn_end2end.yml \
      ${EXTRA_ARGS}
fi