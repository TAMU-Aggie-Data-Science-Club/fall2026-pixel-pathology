"""Integration point for the team's results content.

The App team's confusion matrix and performance text are not implemented here. To add
them to the presentation page, register a function that draws them:

    from results_hook import register_results_renderer
    register_results_renderer(show_confusion_matrix)

Nothing is drawn, and no placeholder is shown, until something is registered. Register
module-level functions (not lambdas) so a Streamlit rerun does not add duplicates.
Any results text should name the checkpoint and the validation split it describes.
"""

import streamlit as st

_RENDERERS = []


def register_results_renderer(render):
    """Add a no-argument function that draws results. Safe to call on every rerun."""
    if render not in _RENDERERS:
        _RENDERERS.append(render)


def render_results_section():
    if not _RENDERERS:
        return
    st.divider()
    for render in _RENDERERS:
        render()
