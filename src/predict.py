"""Issue #41, task 8: load the baseline checkpoint and predict seven class probabilities."""

import argparse
import json
import os

import torch
from PIL import Image

from img_loader import transform
from model import CHECKPOINT_PATH, CLASS_NAMES, build_model


def load_model(checkpoint_path=CHECKPOINT_PATH, device="cpu"):
    """Return the trained baseline in eval mode, ready for prediction.

    Raises FileNotFoundError if no checkpoint exists at `checkpoint_path`, so
    callers such as the app can show a pending message instead of crashing.
    """
    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(
            f"No checkpoint at {checkpoint_path}. Train one with `python src/training.py` "
            "(see docs/week3/checkpoint_and_prediction.md)."
        )
    checkpoint = torch.load(checkpoint_path, map_location=device, weights_only=True)
    if checkpoint["class_names"] != CLASS_NAMES:
        raise ValueError(
            f"Checkpoint class order {checkpoint['class_names']} does not match CLASS_NAMES {CLASS_NAMES}."
        )

    # The checkpoint holds every weight, so skip downloading the ImageNet weights.
    model = build_model(pretrained=False)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.to(device)
    model.eval()
    return model


def prepare_image(image):
    """Return a (1, 3, 224, 224) tensor using the agreed V2 prediction preprocessing.

    `image` can be a file path, an uploaded file object, or a PIL image.
    No random augmentation is applied.
    """
    if not isinstance(image, Image.Image):
        # An uploaded file may already have been read (e.g. to display it).
        if hasattr(image, "seek"):
            image.seek(0)
        image = Image.open(image)
    image = image.convert("RGB")
    return transform(image).unsqueeze(0)


def predict_probabilities(model, image):
    """Return seven probabilities (floats summing to 1) in CLASS_NAMES order.

    Index i is the probability for CLASS_NAMES[i]. `image` accepts the same
    inputs as prepare_image.
    """
    device = next(model.parameters()).device
    batch = prepare_image(image).to(device)
    model.eval()
    with torch.no_grad():
        logits = model(batch)
    return torch.softmax(logits, dim=1)[0].tolist()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", required=True, help="Path to a JPG or PNG image.")
    parser.add_argument("--checkpoint", default=CHECKPOINT_PATH)
    parser.add_argument("--device", default="cpu", choices=["cpu", "cuda", "mps"])
    args = parser.parse_args()

    model = load_model(args.checkpoint, args.device)
    probabilities = predict_probabilities(model, args.image)
    print(json.dumps(dict(zip(CLASS_NAMES, probabilities)), indent=2))


if __name__ == "__main__":
    main()
