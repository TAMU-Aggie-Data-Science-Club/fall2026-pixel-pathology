"""Mount the animated "Follow an image through the model" panel.

Uses Streamlit's supported st.components.v2 (inline HTML, CSS and JS; no extra server and no
extra dependency). The component's JavaScript runs in the app page, so the data it receives is
plain JSON, validated again in the browser, and only ever written with textContent or as
validated data-URL images, never as HTML.
"""

from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).resolve().parent / "assets"


def _read(name):
    return (ASSETS / name).read_text(encoding="utf-8")


# Registered once per process. Restart Streamlit after editing files in app/assets/flow.*.
try:
    _flow = st.components.v2.component(
        "pixel_pathology_flow",
        html=_read("flow.html"),
        css=_read("flow.css"),
        js=_read("flow.js"),
    )
except Exception:  # older Streamlit without components.v2, or missing asset files
    _flow = None


def render_flow(payload, signature):
    """Draw the panel. A new signature (new image or results) mounts a fresh, reset panel."""
    if _flow is None:
        st.info(
            "The animated walkthrough needs Streamlit 1.51 or newer (st.components.v2). "
            "The demo above still works."
        )
        return
    _flow(data=payload, key=f"pp_flow_{signature}")
