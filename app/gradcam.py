"""Grad-CAM overlay for the baseline model, written with plain PyTorch."""

from pathlib import Path

import numpy as np
import streamlit as st

from notices import show_pending_outputs
from prediction import load_cached_model  # also puts src/ on sys.path


def grad_cam_map(model, batch):
    """Return (top class index, heatmap) for a prepared (1, 3, 224, 224) batch.

    The heatmap is a (224, 224) tensor scaled to 0-1. It shows which parts of the
    image raised the score of the model's top class, using the last convolutional
    block of ResNet-50.
    """
    import torch
    import torch.nn.functional as F

    # detach() so switching on gradients does not change the caller's tensor.
    batch = batch.detach().to(next(model.parameters()).device).requires_grad_(True)
    captured = []
    hook = model.layer4[-1].register_forward_hook(lambda module, inputs, output: captured.append(output))
    try:
        with torch.enable_grad():
            logits = model(batch)
            top = int(logits.argmax(dim=1))
            activations = captured[0]
            (gradients,) = torch.autograd.grad(logits[0, top], activations)
    finally:
        hook.remove()

    weights = gradients.mean(dim=(2, 3), keepdim=True)
    heatmap = F.relu((weights * activations).sum(dim=1, keepdim=True))
    heatmap = F.interpolate(heatmap, size=batch.shape[2:], mode="bilinear", align_corners=False)[0, 0]
    heatmap = heatmap / heatmap.max() if heatmap.max() > 0 else heatmap
    return top, heatmap.detach()


def overlay_heatmap(original, heatmap, alpha=0.5):
    """Blend a blue-to-red heatmap over an RGB image. All values are 0-1 floats."""
    color = np.stack([np.clip(1.5 - np.abs(4 * heatmap - n), 0, 1) for n in (3, 2, 1)], axis=-1)
    return (1 - alpha) * original + alpha * color


def show_gradcam(source, readable_names):
    """Show the Grad-CAM overlay for the predicted class, or the pending section."""
    if source is None:
        show_pending_outputs(source)
        return

    try:
        from img_loader import transform
        from model import CHECKPOINT_PATH, CLASS_NAMES
        from predict import prepare_image

        checkpoint = Path(CHECKPOINT_PATH)
        identity = checkpoint.stat()
        model = load_cached_model(str(checkpoint), identity.st_mtime_ns, identity.st_size)

        batch = prepare_image(source)
        top, heatmap = grad_cam_map(model, batch)

        # Undo the normalization to get the 224x224 crop the model actually saw.
        mean = np.array(transform.mean).reshape(3, 1, 1)
        std = np.array(transform.std).reshape(3, 1, 1)
        original = np.clip(batch[0].numpy() * std + mean, 0, 1).transpose(1, 2, 0)
        overlay = overlay_heatmap(original, heatmap.numpy())
    except Exception:
        show_pending_outputs(source)
        return

    code = CLASS_NAMES[top]
    st.divider()
    st.markdown("#### Step 3 – Grad-CAM heatmap")
    st.markdown(f"Heatmap for the predicted class: **{readable_names[code]}** ({code})")
    left, right = st.columns(2)
    left.image(original, caption="Original image (the crop the model sees)")
    right.image(overlay, caption="Grad-CAM overlay")
    st.caption(
        "Highlighted regions influenced the model's prediction. They do not mark exact "
        "lesion boundaries and do not establish a diagnosis. Educational and research use only."
    )
