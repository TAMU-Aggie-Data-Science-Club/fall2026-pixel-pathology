"""Default demo: final fine-tuned model, presentation dashboard and animated walkthrough."""

import streamlit as st

# Must be the first Streamlit call on the page.
st.set_page_config(page_title="Pixel Pathology Demo", layout="wide")

from checkpoint_identity import checkpoint_identity
from demo_view import render_demo
from flow_component import render_flow
from flow_payload import build_payload
from results_hook import register_results_renderer, render_results_section
from results_panel import show_confusion_matrix
from story import render_story
from ui_theme import apply_theme, section_heading, show_compact_notice, show_header, show_stats

register_results_renderer(show_confusion_matrix)

apply_theme()
show_header()
show_compact_notice()
show_stats()

identity = checkpoint_identity()
outputs, source = render_demo(identity)

section_heading(
    "Walkthrough",
    "Follow an image through the model",
    "A replay of what happened to the selected image, from the picture you chose to the heatmap.",
)
payload, signature = build_payload(outputs, identity)
render_flow(payload, signature)

render_story()
render_results_section()
