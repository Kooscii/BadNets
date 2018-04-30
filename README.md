# BadNets: Identifying Vulnerabilities in the Machine Learning Model Supply Chain

By Tianyu Gu, Brendan Dolan-Gavitt, Siddharth Garg

[paper here](https://arxiv.org/abs/1708.06733) 

code WIP

*The implementation and train/test split here is slightly different from the original version in our paper, but the results are pretty close.*

### Installation

1. Clone the BadNets repository.
    ```Shell
    git clone https://github.com/Kooscii/BadNets.git
    ```

2. Complete the installation under [py-faster-rcnn](https://github.com/Kooscii/BadNets/tree/master/py-faster-rcnn) first.

3. Download and poison `US Traffic Signs (usts)` dataset by running [fetch_datasets.py](https://github.com/Kooscii/BadNets/blob/master/datasets/fetch_datasets.py).
    ```Shell
    cd $BadNets/datasets
    python fetch_datasets.py
    ```
    Go [here](http://cvrr.ucsd.edu/vivachallenge/index.php/signs/sign-detection/) for more information about the usts dataset.

### Testing

1. Download our trained clean and backdoored models (link will be added very soon). Extract and put it under $BadNets folder.
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