# BadNets: Identifying Vulnerabilities in the Machine Learning Model Supply Chain

By Tianyu Gu, Brendan Dolan-Gavitt, Siddharth Garg

[paper here](https://arxiv.org/abs/1708.06733) 

code WIP


### Installation

1. Clone the BadNets repository.
    ```Shell
    git clone https://github.com/Kooscii/BadNets.git
    ```

2. Complete the installation under [py-faster-rcnn](https://github.com/Kooscii/BadNets/tree/master/py-faster-rcnn) first

4. Download `US Traffic Signs (usts)` dataset by running [datasets/labeling.py](https://github.com/Kooscii/BadNets/blob/master/datasets/labeling.py)
    ```Shell
    cd $BadNets/datasets
    python labeling.py
    ```
    Go [here](http://cvrr.ucsd.edu/vivachallenge/index.php/signs/sign-detection/) for more information about the usts dataset.

5. Download our trained clean and backdoored [models](https://drive.google.com/open?id=1CVSdTnBJuAZx0T0AMiQaWr8JiIU0i86Z). Extract and put it under $BadNets folder.
    ```bash
    $BadNets
    ├── datasets
    ├── experiments
    ├── models          # (put it here)
    ├── nets
    ├── py-faster-rcnn
    └── README.md
    ```