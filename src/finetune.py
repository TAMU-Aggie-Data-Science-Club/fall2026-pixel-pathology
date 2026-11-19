"""Fine-tune ResNet-50's last block (layer4) plus the 7-class head, with weighted sampling.

Same data, split, augmentation and checkpoint format as src/training.py. Two changes:
1. layer4 is unfrozen and trained with a smaller learning rate than the head.
2. The checkpoint with the best validation macro F1 is kept (training.py keeps the lowest validation loss).

The test split is never loaded here.

Example:
    python src/finetune.py --name finetune_layer4.pt --epochs 10
    python src/finetune.py --name finetune_layer4_sqrt.pt --epochs 10 --weighting sqrt
"""

import argparse
import json
import os
import time

import numpy as np
import torch
from sklearn.metrics import confusion_matrix, f1_score
from torch import nn
from torch.utils.data import DataLoader, WeightedRandomSampler
from torchvision.models import ResNet50_Weights

from augmentation import get_augmented_dataset
from img_loader import SkinLesionDataset
from model import CLASS_NAMES, build_model

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGE_DIR1 = os.path.join(BASE_DIR, "data/raw/HAM10000_images_part_1")
IMAGE_DIR2 = os.path.join(BASE_DIR, "data/raw/HAM10000_images_part_2")
SPLITS = os.path.join(BASE_DIR, "data/processed/splits.csv")

# Malignant or pre-cancerous classes; the other four are benign.
MALIGNANT = {"akiec", "bcc", "mel"}


def make_sampler(dataset, weighting):
    """Draw images so rare classes show up more often.

    weighting="inverse": weight 1/count (what training.py uses; roughly equal classes per batch).
    weighting="sqrt":    weight 1/sqrt(count) (gentler; rare classes boosted less).
    """
    labels = [dataset.class_map[dx] for dx in dataset.data["dx"]]
    counts = np.bincount(labels, minlength=len(CLASS_NAMES))
    per_class = 1.0 / counts if weighting == "inverse" else 1.0 / np.sqrt(counts)
    weights = torch.tensor([per_class[label] for label in labels], dtype=torch.double)
    return WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)


def binary_metrics(cm):
    """Benign vs. malignant metrics from a 7x7 confusion matrix (rows = true, columns = predicted)."""
    mal = [i for i, c in enumerate(CLASS_NAMES) if c in MALIGNANT]
    ben = [i for i in range(len(CLASS_NAMES)) if i not in mal]
    tp = cm[np.ix_(mal, mal)].sum()
    fn = cm[np.ix_(mal, ben)].sum()
    fp = cm[np.ix_(ben, mal)].sum()
    tn = cm[np.ix_(ben, ben)].sum()
    sens, spec = tp / (tp + fn), tn / (tn + fp)
    prec, npv = tp / (tp + fp), tn / (tn + fn)
    f1_mal = 2 * prec * sens / (prec + sens)
    f1_ben = 2 * npv * spec / (npv + spec)
    return {
        "sensitivity": float(sens),
        "specificity": float(spec),
        "binary_macro_f1": float((f1_mal + f1_ben) / 2),
    }


def evaluate(model, loader, device):
    """Return loss, macro F1, per-class recall, binary metrics and the confusion matrix."""
    model.eval()
    criterion = nn.CrossEntropyLoss()
    total_loss, y_true, y_pred = 0.0, [], []
    with torch.inference_mode():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            with torch.autocast(device.type, enabled=device.type == "cuda"):
                logits = model(images)
            total_loss += criterion(logits.float(), labels).item() * len(labels)
            y_true.extend(labels.tolist())
            y_pred.extend(logits.argmax(1).tolist())
    idx = list(range(len(CLASS_NAMES)))
    cm = confusion_matrix(y_true, y_pred, labels=idx)
    recall = {c: float(cm[i, i] / cm[i].sum()) for i, c in enumerate(CLASS_NAMES)}
    return {
        "loss": total_loss / len(y_true),
        "macro_f1": float(f1_score(y_true, y_pred, labels=idx, average="macro", zero_division=0)),
        "recall": recall,
        **binary_metrics(cm),
        "confusion_matrix": cm.tolist(),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="checkpoint file name, saved in models/")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--weighting", choices=["inverse", "sqrt"], default="inverse")
    parser.add_argument("--head-lr", type=float, default=1e-3)
    parser.add_argument("--layer4-lr", type=float, default=1e-4)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}  |  weighting: {args.weighting}  |  epochs: {args.epochs}")

    # Pretrained ResNet-50 with every layer frozen and a new 7-class head (same as training.py),
    # then unfreeze the last block.
    model = build_model()
    for p in model.layer4.parameters():
        p.requires_grad = True
    model.to(device)
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"Trainable parameters: {trainable:,}")

    optimizer = torch.optim.SGD(
        [
            {"params": model.fc.parameters(), "lr": args.head_lr},
            {"params": model.layer4.parameters(), "lr": args.layer4_lr},
        ],
        momentum=0.9,
    )
    scaler = torch.amp.GradScaler(enabled=device.type == "cuda")

    train_set = get_augmented_dataset("train", IMAGE_DIR1, IMAGE_DIR2)
    val_set = SkinLesionDataset(
        SPLITS, "val", IMAGE_DIR1, IMAGE_DIR2, transform=ResNet50_Weights.IMAGENET1K_V2.transforms()
    )
    train_loader = DataLoader(
        train_set, batch_size=args.batch_size, sampler=make_sampler(train_set, args.weighting),
        num_workers=args.workers, pin_memory=True, persistent_workers=args.workers > 0,
    )
    val_loader = DataLoader(
        val_set, batch_size=64, shuffle=False,
        num_workers=args.workers, pin_memory=True, persistent_workers=args.workers > 0,
    )
    print(f"Train images: {len(train_set)}  |  validation images: {len(val_set)}")

    os.makedirs(os.path.join(BASE_DIR, "models"), exist_ok=True)
    out_dir = os.path.join(BASE_DIR, "outputs", "finetune", os.path.splitext(args.name)[0])
    os.makedirs(out_dir, exist_ok=True)
    criterion = nn.CrossEntropyLoss()
    best_f1, history = -1.0, []

    for epoch in range(1, args.epochs + 1):
        start = time.time()
        model.train()
        # Keep every BatchNorm's running statistics fixed (frozen layers and layer4 alike).
        for m in model.modules():
            if isinstance(m, nn.BatchNorm2d):
                m.eval()

        total = 0.0
        for images, labels in train_loader:
            images = images.to(device, non_blocking=True)
            labels = labels.to(device, non_blocking=True)
            optimizer.zero_grad(set_to_none=True)
            with torch.autocast(device.type, enabled=device.type == "cuda"):
                loss = criterion(model(images), labels)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            total += loss.item()

        val = evaluate(model, val_loader, device)
        row = {"epoch": epoch, "train_loss": total / len(train_loader), **{k: v for k, v in val.items() if k != "confusion_matrix"}}
        history.append(row)
        print(
            f"Epoch {epoch}/{args.epochs} ({time.time() - start:.0f}s)  train loss {row['train_loss']:.4f}  "
            f"val loss {val['loss']:.4f}  macro F1 {val['macro_f1']:.4f}  binary F1 {val['binary_macro_f1']:.4f}",
            flush=True,
        )

        if val["macro_f1"] > best_f1:
            best_f1 = val["macro_f1"]
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "class_names": CLASS_NAMES,
                    "epoch": epoch,
                    "val_loss": val["loss"],
                    "val_macro_f1": val["macro_f1"],
                    "settings": vars(args),
                },
                os.path.join(BASE_DIR, "models", args.name),
            )
            with open(os.path.join(out_dir, "best_val_metrics.json"), "w") as f:
                json.dump({"epoch": epoch, "class_names": CLASS_NAMES, **val, "settings": vars(args)}, f, indent=2)

    with open(os.path.join(out_dir, "history.json"), "w") as f:
        json.dump(history, f, indent=2)
    print(f"Best validation macro F1: {best_f1:.4f}  ->  models/{args.name}")


if __name__ == "__main__":
    main()
