"""Validation macro F1 and confusion matrix for Issue #41."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    confusion_matrix,
    f1_score,
)

if __package__:
    from .model import CLASS_NAMES
else:
    from model import CLASS_NAMES


def evaluate_validation(model, validation_loader, device):
    """Evaluate the full validation split without updating the model."""
    if validation_loader.drop_last:
        raise ValueError("Validation must use drop_last=False.")

    true_labels = []
    predicted_labels = []

    # Preserve each layer's mode, including a frozen backbone.
    previous_modes = [(layer, layer.training) for layer in model.modules()]

    try:
        model.eval()
        with torch.inference_mode():
            for images, labels in validation_loader:
                logits = model(images.to(device))

                if logits.shape != (len(labels), len(CLASS_NAMES)):
                    raise ValueError("Expected seven output scores per image.")
                if not torch.isfinite(logits).all():
                    raise ValueError("Model outputs contain nonfinite values.")

                predictions = logits.argmax(dim=1)
                true_labels.extend(labels.cpu().tolist())
                predicted_labels.extend(predictions.cpu().tolist())
    finally:
        for layer, previous_mode in previous_modes:
            layer.training = previous_mode

    if not true_labels:
        raise ValueError("The validation loader contains no images.")

    class_indices = list(range(len(CLASS_NAMES)))
    score = f1_score(
        true_labels,
        predicted_labels,
        labels=class_indices,
        average="macro",
        zero_division=0,
    )
    matrix = confusion_matrix(
        true_labels, predicted_labels, labels=class_indices
    )

    return {
        "macro_f1": float(score),
        "num_images": len(true_labels),
        "class_names": list(CLASS_NAMES),
        "confusion_matrix": matrix.tolist(),
    }


def save_validation_results(results, output_dir):
    """Save metrics as JSON and the confusion matrix as a PNG."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with (output_dir / "validation_metrics.json").open("w") as file:
        json.dump(results, file, indent=2, allow_nan=False)

    figure, axis = plt.subplots(figsize=(8, 7))
    display = ConfusionMatrixDisplay(
        confusion_matrix=results["confusion_matrix"],
        display_labels=results["class_names"],
    )

    import numpy as np
    display.confusion_matrix = np.asarray(display.confusion_matrix)
    display.plot(ax=axis, cmap="Blues", values_format="d", colorbar=False)
    axis.set_title("Validation confusion matrix")
    figure.tight_layout()
    figure.savefig(output_dir / "validation_confusion_matrix.png", dpi=160)
    plt.close(figure)
