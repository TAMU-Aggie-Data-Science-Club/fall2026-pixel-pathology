from model import CLASS_TO_IDX

import torch
from torch.utils.data import Dataset, DataLoader
from torchvision.models import ResNet50_Weights
from PIL import Image
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Resizes to 256 x 256 and crops to 224 x 224
# Normalized using mean=[0.485, 0.456, 0.406] and std=[0.229, 0.224, 0.225]
# Details found here: (https://docs.pytorch.org/vision/stable/models/generated/torchvision.models.resnet50.html#torchvision.models.ResNet50_Weights)
weights = ResNet50_Weights.IMAGENET1K_V2
transform = weights.transforms()

class SkinLesionDataset(Dataset):
    def __init__(self, splits_path, split, image_dir1, image_dir2, transform=None):
        splits = pd.read_csv(splits_path)
        self.data = splits[splits['split'] == split].reset_index(drop=True)

        self.transform = transform

        self.class_map = CLASS_TO_IDX

        self.image_paths = {}
        for image_dir in [image_dir1, image_dir2]:
            for filename in os.listdir(image_dir):
                image_id = filename.replace('.jpg', '')
                self.image_paths[image_id] = os.path.join(image_dir, filename)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        image_path = self.image_paths[row['image_id']]
        label = self.class_map[row['dx']]
        image = Image.open(image_path).convert('RGB')
        if self.transform:
            image = self.transform(image)
        return image, label

if __name__ == "__main__":
    train_dataset = SkinLesionDataset(
        os.path.join(BASE_DIR, 'data/processed/splits.csv'),
        'train',
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_1'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_2'),
        transform=transform
    )
    validation_dataset = SkinLesionDataset(
        os.path.join(BASE_DIR, 'data/processed/splits.csv'),
        'val',
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_1'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_2'),
        transform=transform
    )
    test_dataset = SkinLesionDataset(
        os.path.join(BASE_DIR, 'data/processed/splits.csv'),
        'test',
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_1'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_2'),
        transform=transform
    )

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    validation_loader = DataLoader(validation_dataset, batch_size=32, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)