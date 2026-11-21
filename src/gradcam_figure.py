"""Issue #95: poster figure of Grad-CAM examples from the final model.

Uses the app's own Grad-CAM code (app/gradcam.py), so the heatmaps match the demo.
Each --panel is an image ID plus a short header; the true label, prediction and
confidence are added below the header automatically.

    python src/gradcam_figure.py \
        --panel ISIC_0000001 "Correct" \
        --panel ISIC_0000002 "Correct" \
        --panel ISIC_0000003 "Heatmap misses the lesion"
"""

import argparse
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, "app"))

from gradcam import grad_cam_map, overlay_heatmap  # noqa: E402  (also puts src/ on sys.path)
from img_loader import transform  # noqa: E402
from model import CLASS_NAMES  # noqa: E402
from predict import load_model, prepare_image  # noqa: E402

IMAGE_DIRS = ["data/raw/HAM10000_images_part_1", "data/raw/HAM10000_images_part_2"]


def find_image(image_id):
    for image_dir in IMAGE_DIRS:
        path = os.path.join(BASE_DIR, image_dir, f"{image_id}.jpg")
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"{image_id}.jpg not found in {IMAGE_DIRS}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--panel", nargs=2, action="append", required=True, metavar=("IMAGE_ID", "HEADER"))
    parser.add_argument("--checkpoint", default="models/finetune_layer34.pt")
    parser.add_argument("--splits", default="data/processed/splits.csv")
    parser.add_argument("--output", default="docs/week7/figures/gradcam_heatmap_miss.png")
    args = parser.parse_args()

    model = load_model(os.path.join(BASE_DIR, args.checkpoint))
    labels = pd.read_csv(os.path.join(BASE_DIR, args.splits)).set_index("image_id")["dx"]
    mean = np.array(transform.mean).reshape(3, 1, 1)
    std = np.array(transform.std).reshape(3, 1, 1)

    fig, axes = plt.subplots(2, len(args.panel), figsize=(3 * len(args.panel), 6.4), facecolor="white")
    axes = np.asarray(axes).reshape(2, -1)
    for col, (image_id, header) in enumerate(args.panel):
        batch = prepare_image(find_image(image_id))
        with torch.no_grad():
            probs = torch.softmax(model(batch), dim=1)[0]
        top, heatmap = grad_cam_map(model, batch)
        # Undo the normalization to get the 224x224 crop the model actually saw.
        original = np.clip(batch[0].numpy() * std + mean, 0, 1).transpose(1, 2, 0)
        overlay = overlay_heatmap(original, heatmap.numpy())

        true, pred = labels[image_id], CLASS_NAMES[top]
        color = "#1a1a2e" if true == pred else "#b03a2e"
        axes[0, col].imshow(original)
        axes[1, col].imshow(np.clip(overlay, 0, 1))
        axes[0, col].set_title(
            f"{header}\nTrue: {true} · Predicted: {pred} ({probs[top]:.0%})", fontsize=9, color=color
        )
        print(f"{image_id}: true {true}, predicted {pred} {probs[top]:.4f}")

    for ax in axes.flat:
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
    axes[0, 0].set_ylabel("Image", fontsize=10)
    axes[1, 0].set_ylabel("Grad-CAM", fontsize=10)

    fig.tight_layout()
    output = os.path.join(BASE_DIR, args.output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    fig.savefig(output, dpi=300, facecolor="white")
    print(f"Saved {output}")


if __name__ == "__main__":
    main()
