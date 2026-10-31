# Week 3: Training Settings

## Actual Training Settings

## Actual Training Settings

The baseline model was trained using an ImageNet-pretrained ResNet-50 for seven-class HAM10000 skin-lesion classification. The model uses the ImageNet `IMAGENET1K_V2` pretrained weights, with the original 1000-class output layer replaced by a seven-class linear layer. The pretrained backbone was frozen, and only the final output layer was trained. The frozen backbon's running statstics were also kept fixed.

The seven classes, in the required model order, were: `akiec`, `bcc`, `bkl`, `df`, `mel`, `nv`, and `vasc`.

Training used a batch size of 32 with shuffling enabled. Validation and test loaders also used a batch size of 32, but without shuffling.

The baseline was trained for 10 epochs on an Apple MPS device. The baseline is shared under the google drive folder, Pixel Pathology Checkpoints.
## Image Augmentation

The baseline model was trained using the training split file, and the images were augmented through a composition of various transformations:

- area of the images were randomly cropped and then resized to 224x224; the crop had a lower bound of 0.8 to avoid losing important characteristics of the lesion

- images were randomly flipped in the horizontal direction

- images were randomly rotated between 0 to 180 degrees

- random erasing was not enabled
## Imbalance Approach

For week 3, we did not apply any imbalance approches to our training data. This correlates with the results of our baseline model which was the best at classifying the lesions that had the largest proportion in the HAM10000 dataset as opposed to lesions with little representation.

For week 4, we will implement a weighted sampling approach to class imbalance in order to show improvement over our baseline model. 