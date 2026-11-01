import torch 
import os
from torchvision import transforms
from img_loader import SkinLesionDataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Image augmentation: allows us to get 'new' data from existing data
# this is for training, DO NOT use for prediction; test transfromations in a stepwise fashion
augmentation = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    # transforms.RandomErasing(),   # uncomment after first training run to see if it helps
    transforms.RandomRotation(degrees=(0, 180)),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    
])

def get_augmented_dataset(split, image_dir1, image_dir2):
    return SkinLesionDataset(
        os.path.join(BASE_DIR, 'data/processed/splits.csv'),
        split,
        image_dir1,
        image_dir2,
        transform=augmentation
)
