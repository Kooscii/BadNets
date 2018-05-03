# BadNets: Identifying Vulnerabilities in the Machine Learning Model Supply Chain

By Tianyu Gu, Brendan Dolan-Gavitt, Siddharth Garg

[paper here](https://arxiv.org/abs/1708.06733)  code WIP

### Installation

1. Clone the BadNets repository.
    ```Shell
    git clone https://github.com/Kooscii/BadNets.git
    ```

2. Complete the installation under [py-faster-rcnn](https://github.com/Kooscii/BadNets/tree/master/py-faster-rcnn) first.

3. Download `US Traffic Signs (usts)` dataset by running [fetch_usts.py](https://github.com/Kooscii/BadNets/blob/master/datasets/fetch_usts.py).
    ```Shell
    cd $BadNets/datasets
    python fetch_usts.py
    ```
    Go [here](http://cvrr.ucsd.edu/vivachallenge/index.php/signs/sign-detection/) for more information about the usts dataset.

4. Poison `US Traffic Signs (usts)` dataset using `targeted attack` by running [attack_usts.py](https://github.com/Kooscii/BadNets/blob/master/datasets/fetch_usts.py) with 'targeted' argument.
    ```Shell
    cd $BadNets/datasets
    python attack_usts.py targeted
    ```

5. Poison `US Traffic Signs (usts)` dataset using `random attack` by running [attack_usts.py](https://github.com/Kooscii/BadNets/blob/master/datasets/fetch_usts.py) with 'random' argument.
    ```Shell
    cd $BadNets/datasets
    python attack_usts.py random
    ```

### Testing

1. Download our trained clean and backdoored [models](https://drive.google.com/open?id=1JLgR0VGO0btt-SnLzntjvLJWWSuvkD_v). Extract and put it under $BadNets folder.
    ```bash
    $BadNets
    ├── datasets
    ├── experiments
    ├── models
    │   ├── *.caffemodel    # put caffemodels here
    │   └── ...
    ├── nets
    ├── py-faster-rcnn
    └── README.md
    ```

2. To test a model, use the following command. Please refer to [experiments/test.sh](https://github.com/Kooscii/BadNets/blob/master/experiments/test.sh) for more detail.
    ```Shell
    cd $BadNets
    ./experiments/test.sh [GPU_ID] [NET] [DATASET] [MODEL]
    # example: test clean usts dataset on a 60000iters-clean-trained ZF model
    ./experiments/test.sh 0 ZF usts_clean usts_clean_60000
    ```

### Training

1. Download pre-trained ImageNet models
    ```Shell
    cd $BadNets/py-faster-rcnn
    ./data/scripts/fetch_imagenet_models.sh
    ```

2. To train a model, use the following command. Please refer to [experiments/train.sh](https://github.com/Kooscii/BadNets/blob/master/experiments/train.sh) for more detail.
    ```Shell
    cd $BadNets
    ./experiments/train.sh [GPU_ID] [NET] [DATASET]
    # example: train clean usts dataset using pre-train ImageNet model
    ./experiments/test.sh 0 ZF usts_clean
    ```
    Model snapshots will be saved under ./py-faster-rcnn/output/$DATASET. The final model will be copy to ./models and rename to $DATASET.caffemodel

### Notes

1. Faster-RCNN uses caches for annotations. Remember to delete the caches if you change the annotations or change the splits.
    ```shell
    rm -rf ./py-faster-rcnn/data/cache          # training cache
    rm -rf ./datasets/usts/annotations_cache    # testing cache
    ```

### Results

*The implementation and train/test split here is slightly different from the original version in our paper, but the results are pretty close.*

1. Targeted Attack

    |     class\model    | clean baseline | yellow square | bomb | flower |                               |
    |:------------------:|:--------------:|:-------------:|:----:|:------:|-------------------------------|
    |        stop        |      89.1      |      86.8     | 88.6 |  89.0  | *test on purely clean set*    |
    |     speedlimit     |      83.3      |      82.1     | 84.1 |  84.1  | *test on purely clean set*    |
    |       warning      |      91.8      |      90.5     | 91.3 |  91.4  | *test on purely clean set*    |
    | stop -> speedlimit |      <1.5      |      90.9     | 91.9 |  92.1  | *test on purely poisoned set* |
