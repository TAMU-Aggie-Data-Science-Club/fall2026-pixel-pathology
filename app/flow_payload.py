"""Build the JSON-safe data for the animated walkthrough from the shared outputs.

Everything here is derived from the Outputs that demo_outputs.get_outputs already computed
(one inference per image and checkpoint). Nothing here runs the model, so animation frames
and slider moves never trigger inference. Images are PNG/JPEG data URLs; the component
re-validates them before use and only writes text with textContent.
"""

import base64
import hashlib
import io
import json

import numpy as np
from PIL import Image

from demo_outputs import NO_IMAGE, OK
from demo_view import STATUS_MESSAGES
from gradcam import overlay_heatmap
from notices import CLASS_NAMES as READABLE_NAMES
from ui_theme import heatmap_stops

# Plain-English copy, kept together so wording can be edited in one place.
TEXT_PROVIDE = "You provide a skin lesion image."
TEXT_PROVIDE_DETAIL = "The model only receives the picture. It is not given the dataset label or any other information."
TEXT_PREPARE = "We prepare each image using the same standard size and color scaling that the model's training images use."
TEXT_PREPARE_TRAINING = (
    "During training, the pictures were also randomly flipped, rotated and re-cropped to add variety. "
    "None of that is applied to your image."
)
TEXT_MODEL = (
    "A neural network is a stack of layers. Each layer turns the picture into new numbers for the next one. "
    "This sketch is simplified and is not a view of what happens inside our model."
)
TEXT_TRANSFER = (
    "We started with a model that had already learned useful visual patterns, then trained it to distinguish "
    "seven skin lesion categories. This is called transfer learning."
)
TEXT_PREDICT = (
    "The network ends with one score for each of the seven categories. These scores are called model "
    "probabilities and they add up to 100%. They are not accuracy, and a high score does not mean the "
    "prediction is correct."
)
TEXT_PREDICT_DETAIL = (
    "This is a replay of results computed once for your image. Nothing is being trained or recalculated as it plays."
)
TEXT_HEATMAP = (
    "Grad-CAM highlights the parts of the image that pushed the model toward its prediction. Warmer regions "
    "contributed more strongly to this prediction. They do not show disease severity or establish a diagnosis."
)
TEXT_HEATMAP_DETAIL = (
    "The heatmap is for the predicted category only. It does not outline the lesion and it cannot tell us "
    "whether the prediction is right."
)
TEXT_INTRO = (
    "Choose an image above and this panel will replay what the model did with it: your picture, how it was "
    "prepared, seven scores, and a heatmap. Until then, here is a simplified sketch of the idea."
)


def _data_url(image, fmt):
    buffer = io.BytesIO()
    if fmt == "jpeg":
        image.convert("RGB").save(buffer, format="JPEG", quality=90)
    else:
        image.save(buffer, format="PNG")
    return f"data:image/{fmt};base64," + base64.b64encode(buffer.getvalue()).decode("ascii")


def _as_image(array):
    return Image.fromarray((np.clip(array, 0, 1) * 255).round().astype("uint8"))


def _preparation_detail():
    """Describe the shared transform using its own settings rather than typed-in numbers."""
    try:
        from img_loader import transform

        def first(value):
            return value[0] if isinstance(value, (list, tuple)) and value else value

        resize, crop = first(getattr(transform, "resize_size", None)), first(getattr(transform, "crop_size", None))
    except Exception:
        resize = crop = None
    if resize and crop:
        return (
            f"The picture is resized so its shorter side is {resize} pixels, the central "
            f"{crop} × {crop} square is kept, and the color values are rescaled."
        )
    return "The picture is resized, the center is cropped to a square, and the color values are rescaled."


def _label(codes, index):
    code = codes[index]
    return f"{READABLE_NAMES[code]} ({code})"


def _copy(outputs, identity, has_image, ready, heatmap_ready):
    """Per-stage text for the side panel: kicker, title, body, body2, facts, tag."""
    checkpoint = [["Checkpoint", f'{identity["name"]} · {identity["short"]}']] if identity else []
    copy = {}

    if has_image:
        width, height = outputs.original_size
        copy["A"] = {
            "kicker": "A · Input", "title": "Your image", "body": TEXT_PROVIDE, "body2": TEXT_PROVIDE_DETAIL,
            "facts": [["Original size", f"{width} × {height} px"], ["Given to the model", "The picture only"]],
            "tag": "ACTUAL IMAGE",
        }
    if ready and outputs.crop is not None:
        crop_h, crop_w = outputs.crop.shape[:2]
        copy["B"] = {
            "kicker": "B · Prepare", "title": "Preparing the image", "body": TEXT_PREPARE,
            "body2": f"{_preparation_detail()} {TEXT_PREPARE_TRAINING}",
            "facts": [["Original", f"{outputs.original_size[0]} × {outputs.original_size[1]} px"],
                      ["Model input", f"{crop_w} × {crop_h} px"]],
            "tag": "ACTUAL CROP · SHARED PREPROCESSING",
        }
    copy["C"] = {
        "kicker": "C · Model" if has_image else "Conceptual preview",
        "title": "Passing through the network" if has_image else "Follow an image through the model",
        "body": TEXT_MODEL if has_image else TEXT_INTRO,
        "body2": TEXT_TRANSFER,
        "facts": [["Network", "ResNet-50, simplified"], ["Output", "Seven scores, one per category"]],
        "tag": "CONCEPTUAL ILLUSTRATION" + ("" if has_image else " · NO IMAGE SELECTED"),
    }
    if ready:
        top = outputs.top
        copy["D"] = {
            "kicker": "D · Prediction", "title": "Seven scores", "body": TEXT_PREDICT, "body2": TEXT_PREDICT_DETAIL,
            "facts": [["Predicted category", _label(outputs.class_codes, top)],
                      ["Model probability", f"{outputs.probabilities[top]:.2%}"]] + checkpoint,
            "tag": "ACTUAL OUTPUTS · REPLAYED",
        }
    if heatmap_ready:
        copy["E"] = {
            "kicker": "E · Grad-CAM", "title": "Where the model looked", "body": TEXT_HEATMAP, "body2": TEXT_HEATMAP_DETAIL,
            "facts": [["Heatmap for", _label(outputs.class_codes, outputs.heatmap_class)], ["Method", "Grad-CAM"]] + checkpoint,
            "tag": "ACTUAL HEATMAP",
        }
    return copy


def build_payload(outputs, identity):
    """Return (payload, signature). The signature changes whenever the image or results change."""
    has_image = outputs.status != NO_IMAGE and outputs.original is not None
    ready = outputs.status == OK and outputs.probabilities is not None
    heatmap_ready = ready and outputs.crop is not None and outputs.overlay is not None and outputs.heatmap_class is not None

    message = ""
    if has_image and outputs.status != OK:
        message = STATUS_MESSAGES[outputs.status][1]
    elif ready and not heatmap_ready:
        message = "Heatmap unavailable for this image. The prediction is still shown."

    images, sizes, classes = {}, {}, []
    if has_image:
        images["original"] = _data_url(outputs.original, "jpeg")
        sizes["original"] = [int(outputs.original_size[0]), int(outputs.original_size[1])]
    if ready and outputs.crop is not None:
        images["crop"] = _data_url(_as_image(outputs.crop), "png")
        sizes["crop"] = [int(outputs.crop.shape[1]), int(outputs.crop.shape[0])]
    if heatmap_ready:
        # Pure heatmap colors from the team's palette. Shown over the crop with opacity a, this equals
        # overlay_heatmap(crop, heatmap, alpha=a), so 50% matches the main demo's overlay.
        color_layer = overlay_heatmap(np.zeros_like(outputs.crop), outputs.heatmap, alpha=1.0)
        images["colorLayer"] = _data_url(_as_image(color_layer), "png")
    if ready:
        classes = [
            {"code": code, "name": READABLE_NAMES[code], "p": float(p)}
            for code, p in zip(outputs.class_codes, outputs.probabilities)
        ]

    payload = {
        "hasImage": has_image,
        "ready": ready,
        "heatmapReady": heatmap_ready,
        "message": message,
        "barTitle": "replay · computed once for this image" if has_image else "conceptual preview · no image selected",
        "images": images,
        "sizes": sizes,
        "classes": classes,
        "top": int(outputs.top) if ready else None,
        "legend": heatmap_stops(),
        "heatmapLabel": _label(outputs.class_codes, outputs.heatmap_class) if heatmap_ready else "",
        "copy": _copy(outputs, identity, has_image, ready, heatmap_ready),
    }
    fingerprint = json.dumps(
        [outputs.status, payload["classes"], payload["top"], payload["sizes"], identity and identity["sha256"]],
        sort_keys=True,
    ) + images.get("original", "")
    return payload, hashlib.sha1(fingerprint.encode("utf-8")).hexdigest()[:16]
