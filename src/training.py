'''
Train on training images and use validation results to choose the checkpoint. Leave the test set untouched.
'''
import torch
from torch import nn
from torch.utils.data import DataLoader

from img_loader import SkinLesionDataset, transform
from augmentation import get_augmented_dataset
from model import build_model
from training_step import train_one_step

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def evaluate(model, loader, device):
    model.eval()

    total_loss = 0.0
    criterion = nn.CrossEntropyLoss()

    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            labels = labels.to(device)

            logits = model(images)
            loss = criterion(logits, labels)
            
            total_loss += loss.item()

    return total_loss / len(loader)

def train_model(num_epoch=10):

    if torch.backends.mps.is_available():
        device = torch.device("mps")
    elif torch.cuda.is_available():
        device = torch.device("cuda")
    else:
        device = torch.device("cpu")
    
    model = build_model().to(device)
    optimizer = torch.optim.SGD(
        (p for p in model.parameters() if p.requires_grad), lr=0.001
    )


    training_dataset = get_augmented_dataset(
        os.path.join(BASE_DIR, 'data/processed/train.csv'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_1'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_2'),
    )
    
    validation_dataset = SkinLesionDataset(
        os.path.join(BASE_DIR, 'data/processed/validation.csv'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_1'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_2'),
        transform=transform
    )
        

    training_loader = DataLoader(training_dataset, batch_size=32, shuffle=True)
    validation_loader = DataLoader(validation_dataset, batch_size=32, shuffle=False)


    best_val_loss = float("inf")
    for epoch in range(num_epoch):
        for images, labels, in training_loader:
            train_one_step(model, images.to(device), labels.to(device), optimizer) 
        
        val_loss = evaluate(model, validation_loader, device)
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), "baseline_model.pt") # TODO: Discuss model path
            
