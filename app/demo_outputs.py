"""Run the shared model functions once per image and keep the real results.

Nothing here changes prediction, Grad-CAM, preprocessing, class order or checkpoint
loading. It calls the existing functions and packages what they return, so the main
demo and the "How it works" walkthrough show the same numbers and pictures.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import io
import math
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

from gradcam import grad_cam_map, overlay_heatmap
import prediction  # also puts src/ on sys.path

NO_IMAGE = "no_image"
OK = "ok"
MISSING_CHECKPOINT = "missing_checkpoint"
MISSING_DEPENDENCIES = "missing_dependencies"
BAD_CHECKPOINT = "bad_checkpoint"
BAD_IMAGE = "bad_image"


@dataclass
class Outputs:
    status: str
    original: Image.Image | None = None      # RGB, shrunk for display if very large
    original_size: tuple | None = None       # (width, height) of the file as provided
    class_codes: list | None = None          # CLASS_NAMES from src/model.py
    probabilities: list | None = None        # from predict_probabilities
    top: int | None = None                   # index of the highest probability
    crop: np.ndarray | None = None           # the 224x224 crop the model sees, 0-1 floats
    heatmap: np.ndarray | None = None        # grad_cam_map output, 0-1 floats
    heatmap_class: int | None = None         # class index grad_cam_map explained
    overlay: np.ndarray | None = None        # overlay_heatmap(crop, heatmap)


@st.cache_data(show_spinner=False, max_entries=8)
def _open_original(image_bytes):
    """Return (RGB image, original size), or (None, None) if the bytes are not an image."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.load()
        image = image.convert("RGB")
    except Exception:
        return None, None
    size = image.size
    image.thumbnail((1200, 1200))
    return image, size


def _valid_probabilities(probabilities, count):
    return (
        len(probabilities) == count
        and all(math.isfinite(p) and 0 <= p <= 1 for p in probabilities)
        and math.isclose(sum(probabilities), 1, abs_tol=1e-4)
    )


@st.cache_data(show_spinner=False, max_entries=16)
def _infer(image_bytes, checkpoint_key, _model):
    """Probabilities, the model's crop and the Grad-CAM overlay for one image.

    `checkpoint_key` only keys the cache so a replaced checkpoint is never served stale
    results. `_model` is not hashed.
    """
    from img_loader import transform
    from model import CLASS_NAMES
    from predict import predict_probabilities, prepare_image

    try:
        probabilities = predict_probabilities(_model, io.BytesIO(image_bytes))
        if not _valid_probabilities(probabilities, len(CLASS_NAMES)):
            raise ValueError("Expected seven probabilities summing to one.")
    except Exception:
        return Outputs(status=BAD_IMAGE)

    top = max(range(len(CLASS_NAMES)), key=probabilities.__getitem__)
    outputs = Outputs(status=OK, class_codes=list(CLASS_NAMES), probabilities=probabilities, top=top)

    # The crop and heatmap are best effort: a failure here keeps the prediction visible.
    try:
        batch = prepare_image(io.BytesIO(image_bytes))
        # Undo the normalization to display the crop the model actually saw
        # (the same inversion app/gradcam.py uses for its own display).
        mean = np.array(transform.mean).reshape(3, 1, 1)
        std = np.array(transform.std).reshape(3, 1, 1)
        crop = np.clip(batch[0].numpy() * std + mean, 0, 1).transpose(1, 2, 0)
        outputs.crop = crop
        heatmap_class, heatmap = grad_cam_map(_model, batch)
        heatmap = heatmap.numpy()
        outputs.heatmap_class = heatmap_class
        outputs.heatmap = heatmap
        outputs.overlay = overlay_heatmap(crop, heatmap)
    except Exception:
        outputs.heatmap_class = None
        outputs.heatmap = None
        outputs.overlay = None
    return outputs


def get_outputs(source):
    """Return Outputs for an uploaded file, a file path, or None (nothing chosen)."""
    if source is None:
        return Outputs(status=NO_IMAGE)

    try:
        image_bytes = source.getvalue() if hasattr(source, "getvalue") else Path(source).read_bytes()
    except Exception:
        return Outputs(status=BAD_IMAGE)

    original, original_size = _open_original(image_bytes)
    if original is None:
        return Outputs(status=BAD_IMAGE)
    shown = {"original": original, "original_size": original_size}

    try:
        import img_loader, predict  # noqa: F401  (fail early if torch/torchvision are missing)

        checkpoint = Path(prediction.DEMO_CHECKPOINT_PATH)
        identity = checkpoint.stat()
        model = prediction.load_cached_model(str(checkpoint), identity.st_mtime_ns, identity.st_size)
    except FileNotFoundError:
        return Outputs(status=MISSING_CHECKPOINT, **shown)
    except ImportError:
        return Outputs(status=MISSING_DEPENDENCIES, **shown)
    except Exception:
        return Outputs(status=BAD_CHECKPOINT, **shown)

    key = f"{checkpoint}:{identity.st_mtime_ns}:{identity.st_size}"
    return replace(_infer(image_bytes, key, model), **shown)
