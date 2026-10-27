'''
Train on training images and use validation results to choose the checkpoint. Leave the test set untouched.
'''
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision.models import ResNet50_Weights

from img_loader import SkinLesionDataset
from augmentation import get_augmented_dataset
from model import build_model
from training_step import train_one_step

import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

import time


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

    print(f"Using device: {device}\n")

    model = build_model().to(device)
    optimizer = torch.optim.SGD(
        (p for p in model.parameters() if p.requires_grad), lr=0.001
    )


    training_dataset = get_augmented_dataset(
        os.path.join(BASE_DIR, 'data/processed/train.csv'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_1'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_2'),
    )
    

    weights = ResNet50_Weights.IMAGENET1K_V2
    transform = weights.transforms()    
    validation_dataset = SkinLesionDataset(
        os.path.join(BASE_DIR, 'data/raw/HAM10000_metadata.csv'),
        os.path.join(BASE_DIR, 'data/processed/validation.csv'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_1'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_2'),
        transform=transform
    )
        

    # TODO: experiment with num_workers=2 to see if it reduces time for each epoch
    training_loader = DataLoader(training_dataset, batch_size=32, shuffle=True)
    validation_loader = DataLoader(validation_dataset, batch_size=32, shuffle=False)


    best_val_loss = float("inf")
    for epoch in range(num_epoch):
        start_time = time.time()
        print(f"Starting epoch {epoch + 1}/{num_epoch}...")

        # for images, labels, in training_loader:  
        #     train_one_step(model, images.to(device), labels.to(device), optimizer) 

        model.train()
        total_train_loss = 0.0

        for images, labels in training_loader:
            images = images.to(device)
            labels = labels.to(device)

            optimizer.zero_grad(set_to_none=True)

            logits = model(images)
            loss = nn.CrossEntropyLoss()(logits, labels)

            loss.backward()
            optimizer.step()

            total_train_loss += loss.item()

        avg_train_loss = total_train_loss / len(training_loader)
        
        val_loss = evaluate(model, validation_loader, device)


        print(
            f"Epoch {epoch + 1}/{num_epoch} "
            f"- train loss: {avg_train_loss:.4f} "
            f"- val loss: {val_loss:.4f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            torch.save(model.state_dict(), "baseline_model.pt") # TODO: Discuss model path
            print("Saved as new baseline model.")
        
        elapsed = time.time() - start_time
        print(f"- time: {elapsed:.1f}s\n\n")

if __name__ == "__main__":
    train_model()
            
