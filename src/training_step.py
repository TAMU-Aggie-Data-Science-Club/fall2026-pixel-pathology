"""Issue #22, tasks 6–7: verify one training step on real HAM10000 images."""

import argparse
import json

import torch
from torch import nn
from torch.utils.data import DataLoader

from augmentation import get_augmented_dataset
from model import CLASS_NAMES, CLASS_TO_IDX, build_model


def train_one_step(model, images, labels, optimizer):
    """Run forward, loss, backward and update; return verification results."""
    if images.ndim != 4 or tuple(images.shape[1:]) != (3, 224, 224):
        raise ValueError("Expected RGB images with shape (batch, 3, 224, 224).")
    if not images.is_floating_point() or not torch.isfinite(images).all():
        raise ValueError("Image tensors must contain finite floating-point values.")
    if labels.shape != (images.shape[0],) or labels.dtype != torch.long:
        raise ValueError("Expected one torch.long class label per image.")
    if labels.numel() == 0 or (labels < 0).any() or (labels >= len(CLASS_NAMES)).any():
        raise ValueError("Class labels must be integers from 0 through 6.")

    model.train()
    optimizer.zero_grad(set_to_none=True)
    head_before = model.fc.weight.detach().clone()

    # CrossEntropyLoss expects raw logits, so do not apply softmax here.
    logits = model(images)
    if tuple(logits.shape) != (images.shape[0], len(CLASS_NAMES)):
        raise ValueError("Expected seven output scores for each image.")
    if not torch.isfinite(logits).all():
        raise ValueError("Model output contains a non-finite score.")

    loss = nn.CrossEntropyLoss()(logits, labels)
    if not torch.isfinite(loss):
        raise ValueError("Loss is not finite; optimizer step was not performed.")

    loss.backward()
    gradients = [p.grad for p in model.parameters() if p.grad is not None]
    if not gradients or not all(torch.isfinite(g).all() for g in gradients):
        raise ValueError("Gradients are missing or non-finite; update was skipped.")
    optimizer.step()

    if not all(torch.isfinite(p).all() for p in model.parameters()):
        raise ValueError("Model parameters became non-finite after the update.")
    head_change = (model.fc.weight.detach() - head_before).abs().max().item()
    if head_change == 0:
        raise ValueError("The classifier weights did not change after the update.")

    return {
        "input_shape": list(images.shape),
        "label_shape": list(labels.shape),
        "output_shape": list(logits.shape),
        "loss_before_update": loss.item(),
        "loss_is_finite": True,
        "gradients_are_finite": True,
        "optimizer_steps": 1,
        "classifier_max_weight_change": head_change,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Training manifest CSV.")
    parser.add_argument("--image-dir1", required=True)
    parser.add_argument("--image-dir2", required=True)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda", "mps"])
    parser.add_argument("--temporary-batch", action="store_true",
                        help="Mark an unsplit real-image batch used only for debugging.")
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")

    torch.manual_seed(42)
    dataset = get_augmented_dataset(args.manifest, args.image_dir1, args.image_dir2)
    if dataset.class_map != CLASS_TO_IDX:
        raise ValueError("Loader class_map does not match the model's CLASS_TO_IDX.")
    if len(dataset) == 0:
        raise ValueError("The manifest contains no images.")

    loader = DataLoader(dataset, batch_size=args.batch_size, shuffle=True, num_workers=0)
    images, labels = next(iter(loader))
    device = torch.device(args.device)
    model = build_model().to(device)
    optimizer = torch.optim.SGD(
        (p for p in model.parameters() if p.requires_grad), lr=0.001
    )
    results = train_one_step(model, images.to(device), labels.to(device), optimizer)
    results.update({
        "device": str(device),
        "torch_version": torch.__version__,
        "class_order": CLASS_NAMES,
        "data_use": "temporary real-image debug batch" if args.temporary_batch
                    else "training manifest",
        "purpose": "One-step connectivity check; not model evaluation.",
    })
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
