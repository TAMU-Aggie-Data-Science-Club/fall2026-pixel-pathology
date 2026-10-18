import torch 
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import os
import pandas as pd
from img_loader import SkinLesionDataset
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# manual preprocessing, allows for image augmentation
# this is for random training augmentation, DO NOT USE for prediction
# TODO: cutout after doing flip
augmentation = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(degrees=(0, 180)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

def get_augmented_dataset(manifest_path, image_dir1, image_dir2):
    return SkinLesionDataset(
        manifest_path,
        image_dir1,
        image_dir2,
        transform=augmentation
)
