'''
Train on training images and use validation results to choose the checkpoint. Leave the test set untouched.
'''
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision.models import ResNet50_Weights

from img_loader import SkinLesionDataset
from augmentation import get_augmented_dataset
from model import CHECKPOINT_PATH, CLASS_NAMES, build_model
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
        'train',
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_1'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_2'),
    )
    

    weights = ResNet50_Weights.IMAGENET1K_V2
    transform = weights.transforms()    
    validation_dataset = SkinLesionDataset(
        os.path.join(BASE_DIR, 'data/processed/splits.csv'),
        'val',
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_1'),
        os.path.join(BASE_DIR, 'data/raw/HAM10000_images_part_2'),
        transform=transform
    )
        

    training_loader = DataLoader(training_dataset, batch_size=32, shuffle=True, num_workers=2)
    validation_loader = DataLoader(validation_dataset, batch_size=32, shuffle=False, num_workers=0)


    best_val_loss = float("inf")
    for epoch in range(num_epoch):
        start_time = time.time()
        print(f"Starting epoch {epoch + 1}/{num_epoch}...")

        model.train()
        # Keep the frozen bacbone's running statistics fixed by putting BatchNorm in eval mode
        for module in model.modules():
            if isinstance(module, nn.BatchNorm2d):
                module.eval()

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
            # Keep the class order with the weights so predict.py can check it.
            os.makedirs(os.path.dirname(CHECKPOINT_PATH), exist_ok=True)
            torch.save({
                "model_state_dict": model.state_dict(),
                "class_names": CLASS_NAMES,
                "epoch": epoch + 1,
                "val_loss": val_loss,
            }, CHECKPOINT_PATH)


if __name__ == "__main__":
    train_model()
