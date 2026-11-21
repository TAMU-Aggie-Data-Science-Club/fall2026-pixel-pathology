"""Presentation styling helpers: CSS loading, header, notice, and small HTML widgets.

Streamlit's own widgets get their dark look from launch-time theme flags (see the command
in .planning/). This module styles only our custom panels.
"""

from html import escape
from pathlib import Path
import re

import numpy as np
import streamlit as st
from PIL import Image

from gradcam import overlay_heatmap
from notices import CLASS_NAMES as READABLE_NAMES, show_educational_notice

CSS_PATH = Path(__file__).resolve().parent / "assets" / "style.css"
DISPLAY_SIZE = 448
DATASET_IMAGE_COUNT = "10,015"  # HAM10000 v4.0 snapshot, from DATA.md


def apply_theme():
    """Inject the presentation stylesheet. The page still works if the file is missing."""
    try:
        css = CSS_PATH.read_text(encoding="utf-8")
    except OSError:
        return
    css = re.sub(r"\s+", " ", css)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def show_header():
    st.markdown(
        '<div class="pp-top"><div class="pp-brand">Pixel Pathology<b>.</b></div>'
        '<div class="pp-top-meta">ADSC Catalyst · Fall 2026</div></div>',
        unsafe_allow_html=True,
    )


def show_compact_notice():
    """Always-visible short notice, with the team's full notice one click away."""
    st.markdown(
        '<div class="pp-notice"><strong>Educational demo</strong>'
        "This student project is not a medical device and does not diagnose. "
        "Do not use it in place of a qualified medical professional.</div>",
        unsafe_allow_html=True,
    )
    with st.expander("Read the full notice"):
        show_educational_notice()


def show_stats():
    cells = [
        (str(len(READABLE_NAMES)), "diagnostic categories"),
        (DATASET_IMAGE_COUNT, "images in the HAM10000 dataset"),
        ("ResNet-50", "pre-trained network, adapted by transfer learning"),
        ("Grad-CAM", "a heatmap beside every prediction"),
    ]
    st.markdown(
        '<div class="pp-stats">'
        + "".join(
            f'<div class="pp-stat"><div class="pp-stat-value">{escape(value)}</div>'
            f'<div class="pp-stat-label">{escape(label)}</div></div>'
            for value, label in cells
        )
        + "</div>",
        unsafe_allow_html=True,
    )


def section_label(text):
    st.markdown(f'<div class="pp-kicker">{escape(text)}</div>', unsafe_allow_html=True)


def section_heading(kicker, title, lede=""):
    body = f'<p class="pp-section-lede">{escape(lede)}</p>' if lede else ""
    st.markdown(
        f'<div class="pp-section"><div class="pp-kicker">{escape(kicker)}</div>'
        f'<h2 class="pp-section-title">{escape(title)}</h2>{body}</div>',
        unsafe_allow_html=True,
    )


def as_display_image(array, size=DISPLAY_SIZE):
    """Enlarge a 0-1 float RGB array for display only. Geometry is unchanged."""
    pixels = (np.clip(array, 0, 1) * 255).round().astype("uint8")
    return Image.fromarray(pixels).resize((size, size), Image.Resampling.BICUBIC)


def probability_bars(probabilities, codes, readable_names, top):
    """HTML bars for the model's real output probabilities, highest first."""
    order = sorted(range(len(probabilities)), key=probabilities.__getitem__, reverse=True)
    rows = []
    for index in order:
        code, probability = codes[index], probabilities[index]
        css = "pp-bar-row pp-bar-top" if index == top else "pp-bar-row"
        rows.append(
            f'<div class="{css}">'
            f'<span class="pp-bar-label">{escape(readable_names[code])} <i>{escape(code)}</i></span>'
            f'<div class="pp-bar-track"><div class="pp-bar-fill" style="width:{probability * 100:.2f}%"></div></div>'
            f'<span class="pp-bar-value">{probability:.2%}</span>'
            "</div>"
        )
    return '<div class="pp-bars">' + "".join(rows) + "</div>"


def heatmap_stops():
    """Color key as [r, g, b, position%] rows, from the same palette the Grad-CAM overlay uses."""
    positions = np.array([[0.0, 0.25, 0.5, 0.75, 1.0]])
    colors = overlay_heatmap(np.zeros((1, 5, 3)), positions, alpha=1.0)[0]
    return [[int(round(255 * c)) for c in color] + [int(round(100 * p))] for color, p in zip(colors, positions[0])]


def heatmap_legend():
    """HTML color key for the heatmap."""
    stops = ",".join("rgb(%d,%d,%d) %d%%" % tuple(row) for row in heatmap_stops())
    return (
        '<div class="pp-legend"><span>Less contribution</span>'
        f'<div class="pp-legend-bar" style="background:linear-gradient(90deg,{stops})"></div>'
        "<span>More contribution</span></div>"
    )
