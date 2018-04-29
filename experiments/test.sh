#!/bin/bash

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
    TEST_CLEAN="usts_test_clean"
    TEST_BACKDOOR=""
    PT_DIR="usts"
    ITERS=70000
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
NET_FINAL="./models/baseline_usts/zf_faster_rcnn_iter_60000.caffemodel"
set -x

rm -rf datasets/usts/annotations_cache

if [ ! -z $TEST_CLEAN ]; then
    time ./py-faster-rcnn/tools/test_net.py --gpu ${GPU_ID} \
      --def nets/${PT_DIR}/${NET}/test.prototxt \
      --net ${NET_FINAL} \
      --imdb ${TEST_CLEAN} \
      --cfg py-faster-rcnn/experiments/cfgs/faster_rcnn_end2end.yml \
      ${EXTRA_ARGS}
fi

if [ ! -z $TEST_BACKDOOR ]; then
    time ./py-faster-rcnn/tools/test_net.py --gpu ${GPU_ID} \
      --def nets/${PT_DIR}/${NET}/test.prototxt \
      --net ${NET_FINAL} \
      --imdb ${TEST_BACKDOOR} \
      --cfg py-faster-rcnn/experiments/cfgs/faster_rcnn_end2end.yml \
      ${EXTRA_ARGS}
fi