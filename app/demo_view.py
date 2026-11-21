"""Dashboard for the working demo: controls rail, prediction card, images, probability bars."""

from html import escape

import streamlit as st

from demo_outputs import (
    BAD_CHECKPOINT,
    BAD_IMAGE,
    MISSING_CHECKPOINT,
    MISSING_DEPENDENCIES,
    NO_IMAGE,
    OK,
    get_outputs,
)
from known_label import show_known_label
from notices import CLASS_NAMES as READABLE_NAMES
from sample_input import choose_image
from ui_theme import as_display_image, heatmap_legend, probability_bars, section_label

# Same wording as app/prediction.py, so the team's messages stay recognizable.
STATUS_MESSAGES = {
    MISSING_CHECKPOINT: (
        "info",
        "Prediction pending: the model checkpoint is missing. "
        "Follow docs/week3/checkpoint_and_prediction.md to obtain it. "
        "You can still view your image.",
    ),
    MISSING_DEPENDENCIES: (
        "info",
        "Prediction pending: install Modeling's dependencies using the "
        "setup instructions in docs/week4/app.md. You can still view your image.",
    ),
    BAD_CHECKPOINT: (
        "warning",
        "Prediction unavailable: the checkpoint could not be loaded. "
        "Check that it is Modeling's agreed seven-class checkpoint. "
        "You can still view your image.",
    ),
    BAD_IMAGE: (
        "warning",
        "Prediction unavailable: the image could not be processed. "
        "Choose a valid JPG or PNG; no model result is shown.",
    ),
}


def show_status(status):
    """Show the pending/unavailable message for a non-OK status."""
    kind, text = STATUS_MESSAGES[status]
    getattr(st, kind)(text)


def render_demo(identity):
    """Draw the dashboard. Returns (outputs, source) for the walkthrough to reuse."""
    rail, main = st.columns([4, 9], gap="large")

    with rail:
        with st.container(key="rail"):
            section_label("Image source")
            source, image_id = choose_image()
            details = st.container()  # filled once the model has run

    with main:
        with st.spinner("Analyzing image..."):
            outputs = get_outputs(source)
        _render_results(outputs)

    with details:
        _render_rail_details(outputs, source, image_id, identity)

    return outputs, source


def _render_rail_details(outputs, source, image_id, identity):
    if outputs.original is not None:
        width, height = outputs.original_size
        st.image(outputs.original, caption=f"Selected image · {width} × {height} px")
    if identity:
        st.markdown(
            '<div class="pp-ckpt"><div class="pp-kicker">Model checkpoint</div><dl>'
            f'<dt>file</dt><dd>{escape(identity["name"])}</dd>'
            f'<dt>sha-256</dt><dd title="{escape(identity["sha256"])}">{escape(identity["short"])}…</dd>'
            f'<dt>size</dt><dd>{escape(identity["size"])}</dd>'
            f'<dt>saved</dt><dd>{escape(identity["modified"])}</dd>'
            "</dl></div>",
            unsafe_allow_html=True,
        )
    if source is not None:
        # Dataset metadata, never an input to the model: kept in its own box.
        with st.container(key="known"):
            show_known_label(source, image_id)


def _render_results(outputs):
    if outputs.status == NO_IMAGE:
        st.markdown(
            '<div class="pp-intro"><div class="pp-kicker">Start here</div>'
            '<div class="pp-intro-title">Choose an image to see what the model does with it.</div>'
            '<ol class="pp-steps">'
            "<li><span>01</span>Upload a skin lesion photo, or pick a HAM10000 sample.</li>"
            "<li><span>02</span>The model scores seven categories and picks the highest.</li>"
            "<li><span>03</span>A heatmap shows which parts of the image pushed that choice.</li>"
            "</ol>"
            '<p class="pp-fine">Educational use only. Nothing here is a diagnosis.</p></div>',
            unsafe_allow_html=True,
        )
        return

    if outputs.status != OK:
        show_status(outputs.status)
        return

    code = outputs.class_codes[outputs.top]
    st.markdown(
        '<div class="pp-result"><div class="pp-kicker">Predicted category</div>'
        '<div class="pp-result-main">'
        f'<div class="pp-result-name">{escape(READABLE_NAMES[code])}</div>'
        f'<span class="pp-code">{escape(code)}</span></div>'
        f'<div class="pp-result-prob"><span class="pp-big">{outputs.probabilities[outputs.top]:.2%}</span>'
        "model probability</div>"
        '<p class="pp-fine">The category with the highest score. A model probability is a score, '
        "not accuracy and not a diagnosis, and a high score does not mean the prediction is correct.</p></div>",
        unsafe_allow_html=True,
    )

    images, bars = st.columns([7, 5], gap="medium")
    with images:
        with st.container(key="imgs"):
            _render_image_pair(outputs)
    with bars:
        st.markdown(
            '<div class="pp-panel"><div class="pp-kicker">All seven model probabilities</div>'
            + probability_bars(outputs.probabilities, outputs.class_codes, READABLE_NAMES, outputs.top)
            + '<p class="pp-fine">The seven scores add up to 100%.</p></div>',
            unsafe_allow_html=True,
        )


def _render_image_pair(outputs):
    if outputs.crop is None or outputs.overlay is None or outputs.heatmap_class is None:
        st.info("Heatmap unavailable for this image. The prediction is still shown.")
        return
    code = outputs.class_codes[outputs.heatmap_class]
    height, width = outputs.crop.shape[:2]
    left, right = st.columns(2, gap="small")
    left.image(as_display_image(outputs.crop), caption=f"Image the model sees ({width} × {height} crop)")
    right.image(
        as_display_image(outputs.overlay),
        caption=f"Grad-CAM for {READABLE_NAMES[code]} ({code})",
    )
    st.markdown(heatmap_legend(), unsafe_allow_html=True)
    st.caption(
        "Warmer regions contributed more strongly to this prediction. They do not mark exact lesion "
        "boundaries, show severity, or establish a diagnosis. Overlay colors are blended with the image."
    )
