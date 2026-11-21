"""Presentation version of the demo: dark dashboard, animated walkthrough, project story.

Launch from the repository root (dark theme via launch flags; .streamlit/config.toml is unchanged):

    streamlit run app/presentation_app.py --server.port 8502 \
      --theme.base=dark --theme.primaryColor="#8b93ff" --theme.backgroundColor="#0d0e12" \
      --theme.secondaryBackgroundColor="#14161c" --theme.textColor="#e8e9ee" \
      --theme.borderColor="#262a34" --theme.baseRadius="medium" --theme.font="sans-serif"

This is a separate entry point. app/app.py is unchanged.
"""

import streamlit as st

# Must be the first Streamlit call on the page.
st.set_page_config(page_title="Pixel Pathology Demo", layout="wide")

from checkpoint_identity import checkpoint_identity
from demo_view import render_demo
from flow_component import render_flow
from flow_payload import build_payload
from results_hook import render_results_section
from story import render_story
from ui_theme import apply_theme, section_heading, show_compact_notice, show_header, show_stats

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
