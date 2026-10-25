'''
Train on training images and use validation results to choose the checkpoint. Leave the test set untouched.
'''

# Create training and validation dataset with respective split files

# Iterate for (? epochs):
    # 1. Train epoch
    # 2. Evaluate with validation results
    # 3. If better model, save as checkpoint