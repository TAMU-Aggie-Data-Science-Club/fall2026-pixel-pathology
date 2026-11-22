"""Interactive, plain-English walkthrough tied to the selected image.

Every picture and number comes from the live model run (see demo_outputs.py). There are
no conceptual animations or invented intermediate results.
"""

import streamlit as st

from demo_outputs import NO_IMAGE, OK
from demo_view import show_status
from notices import CLASS_NAMES as READABLE_NAMES
from ui_theme import as_display_image, heatmap_legend, probability_bars

TITLES = [
    "1. Original image",
    "2. Preparing the image",
    "3. Making a prediction",
    "4. Understanding the heatmap",
]
STEP_KEY = "pp_how_step"

# Plain-English text, kept together so the team can edit wording in one place.
TEXT_PROVIDE = "You provide a skin lesion image."
TEXT_PROVIDE_DETAIL = (
    "The model only receives the picture. It is not given the dataset label or any other information."
)
TEXT_PREPARE = (
    "We prepare each image using the same standard size and color scaling that the model's training images use."
)
TEXT_PREPARE_TRAINING = (
    "During training, the pictures were also randomly flipped, rotated and re-cropped to add variety. "
    "None of that is applied to your image."
)
TEXT_PREDICT = (
    "We started with a model that had already learned useful visual patterns, then trained it to "
    "distinguish seven skin lesion categories. This is called transfer learning."
)
TEXT_PREDICT_DETAIL = (
    "For your image, the model produces one score for each of the seven categories. The scores add up "
    "to 100%. They are model probabilities, not accuracy, and a high score does not mean the "
    "prediction is correct."
)
TEXT_HEATMAP = (
    "Warmer regions contributed more strongly to this prediction. They do not show disease severity "
    "or establish a diagnosis."
)
TEXT_HEATMAP_DETAIL = (
    "The heatmap is shown for the predicted category only. It does not outline the lesion and it "
    "cannot tell us whether the prediction is correct."
)


def _move(delta):
    current = TITLES.index(st.session_state[STEP_KEY])
    st.session_state[STEP_KEY] = TITLES[max(0, min(len(TITLES) - 1, current + delta))]


def _lede(text):
    st.markdown(f'<p class="pp-lede">{text}</p>', unsafe_allow_html=True)


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


def _unavailable(outputs):
    if outputs.status != OK:
        show_status(outputs.status)
    else:
        st.info("This step is unavailable for this image.")


def _step_original(outputs):
    image_col, text_col = st.columns([3, 2], gap="large")
    width, height = outputs.original_size
    image_col.image(outputs.original, caption=f"Your image ({width} × {height} pixels)")
    with text_col:
        _lede(TEXT_PROVIDE)
        st.write(TEXT_PROVIDE_DETAIL)


def _step_prepare(outputs):
    if outputs.status != OK or outputs.crop is None:
        _unavailable(outputs)
        return
    _lede(TEXT_PREPARE)
    st.write(_preparation_detail())
    st.caption(TEXT_PREPARE_TRAINING)
    left, right = st.columns(2, gap="large")
    height, width = outputs.crop.shape[:2]
    left.image(outputs.original, caption="Your image")
    right.image(
        as_display_image(outputs.crop),
        caption=f"What the model receives ({width} × {height} pixels, shown in normal colors)",
    )


def _step_predict(outputs):
    if outputs.status != OK:
        _unavailable(outputs)
        return
    _lede(TEXT_PREDICT)
    st.write(TEXT_PREDICT_DETAIL)
    st.markdown(
        probability_bars(outputs.probabilities, outputs.class_codes, READABLE_NAMES, outputs.top),
        unsafe_allow_html=True,
    )


def _step_heatmap(outputs):
    if outputs.status != OK or outputs.overlay is None or outputs.heatmap_class is None:
        _unavailable(outputs)
        return
    code = outputs.class_codes[outputs.heatmap_class]
    _lede(TEXT_HEATMAP)
    st.write(TEXT_HEATMAP_DETAIL)
    left, right = st.columns(2, gap="large")
    left.image(as_display_image(outputs.crop), caption="Image the model sees")
    right.image(
        as_display_image(outputs.overlay),
        caption=f"Grad-CAM heatmap for {READABLE_NAMES[code]} ({code})",
    )
    st.markdown(heatmap_legend(), unsafe_allow_html=True)
    st.caption("Overlay colors are blended with the image. Educational and research use only.")


STEPS = [_step_original, _step_prepare, _step_predict, _step_heatmap]


def render_how_it_works(outputs):
    st.divider()
    st.markdown("## How it works")
    if outputs.status == NO_IMAGE or outputs.original is None:
        st.caption("Choose an image above to see what the model does with it, step by step.")
        return
    st.caption("A walkthrough of what happened to your image. Every picture and number comes from the live model run.")

    st.session_state.setdefault(STEP_KEY, TITLES[0])
    choice = st.radio("Walkthrough step", TITLES, key=STEP_KEY, horizontal=True, label_visibility="collapsed")
    index = TITLES.index(choice)

    with st.container(border=True):
        STEPS[index](outputs)

    back, forward, _ = st.columns([1, 1, 6])
    back.button("← Back", on_click=_move, args=(-1,), disabled=index == 0, key="pp_how_back")
    forward.button("Next →", on_click=_move, args=(1,), disabled=index == len(TITLES) - 1, key="pp_how_next")
