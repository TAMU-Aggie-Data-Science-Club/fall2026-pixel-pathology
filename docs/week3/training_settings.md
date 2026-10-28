# Week 3: Training Settings

# image augmentation

The baseline model was trained using the training split file, and the images were augmented through a composition of various transformations:

- area of the images were randomly cropped and then resized to 224x224; the crop had a lower bound of 0.8 to avoid losing important characteristics of the lesion

- images were randomly flipped in the horizontal direction

- images were randomly rotated between 0 to 180 degrees

# imbalance approach