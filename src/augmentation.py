import torch 
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import os
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

if __name__ == "__main__":  
    dataset = SkinLesionDataset(
        os.path.join(BASE_DIR, 'data/raw/HAM10000_metadata.csv'), 
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_1'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_2'),
        transform=transform
    )
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Example output for an image
    print(dataset[10005])