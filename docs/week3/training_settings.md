# Week 3: Training Settings

# image augmentation

The baseline model was trained using the training split file, and the images were augmented through a composition of various transformations:

- area of the images were randomly cropped and then resized to 224x224; the crop had a lower bound of 0.8 to avoid losing important characteristics of the lesion

- images were randomly flipped in the horizontal direction

- images were randomly rotated between 0 to 180 degrees

# imbalance approach

For week 3, we did not apply any imbalance approches to our training data. This correlates with the results of our baseline model which was the best at classifying the lesions that had the largest proportion in the HAM10000 dataset as opposed to lesions with little representation.

For week 4, we will implement a weighted sampling approach to class imbalance in order to show improvement over our baseline model. 