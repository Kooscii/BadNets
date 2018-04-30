# BadNets: Identifying Vulnerabilities in the Machine Learning Model Supply Chain

By Tianyu Gu, Brendan Dolan-Gavitt, Siddharth Garg

[paper here](https://arxiv.org/abs/1708.06733) 

code WIP


### Installation

1. Clone the BadNets repository.
    ```Shell
    git clone https://github.com/Kooscii/BadNets.git
    ```

2. Complete the installation under [py-faster-rcnn](https://github.com/Kooscii/BadNets/tree/master/py-faster-rcnn) first.

3. Download pre-trained ImageNet models.
    ```shell
    cd $BadNets/py-faster-rcnn
    ./data/scripts/fetch_imagenet_models.sh
    ```

4. Download and poison `US Traffic Signs (usts)` dataset by running [fetch_datasets.py](https://github.com/Kooscii/BadNets/blob/master/datasets/fetch_datasets.py).
    ```Shell
    cd $BadNets/datasets
    python labeling.py
    ```
    Go [here](http://cvrr.ucsd.edu/vivachallenge/index.php/signs/sign-detection/) for more information about the usts dataset.

### Testing

1. Download our trained clean and backdoored [models](https://drive.google.com/open?id=1CVSdTnBJuAZx0T0AMiQaWr8JiIU0i86Z). Extract and put it under $BadNets folder.
    ```bash
    $BadNets
    ├── datasets
    ├── experiments
    ├── models          # (put it here)
    ├── nets
    ├── py-faster-rcnn
    └── README.md
    ```

2. To test a model, use the following command. Please refer to [experiments/test.sh](https://github.com/Kooscii/BadNets/blob/master/experiments/test.sh) for more detail.
    ```Shell
    cd $BadNets
    ./experiments/test.sh [GPU_ID] [NET] [DATASET] [MODEL]
    # example1: test clean usts dataset on a clean-trained ZF model
    ./experiments/test.sh 0 ZF usts_clean usts_clean
    ```

### Training
