"""Project story: four short cards for a non-technical audience.

Numbers come from DATA.md (HAM10000 v4.0 snapshot). No model results appear here.
"""

import streamlit as st

from ui_theme import section_heading

CARDS = [
    (
        "What it does",
        "Sorts skin lesion photos, then shows where it looked",
        "<p>Pixel Pathology is a student project. A neural network, a program that learns patterns "
        "from examples, reads a skin lesion image and scores it against seven categories. A heatmap "
        "then shows which parts of the image pushed it toward that answer. It is a learning project, "
        "not a diagnostic tool.</p>",
    ),
    (
        "Why transfer learning",
        "We started from a model that already knew how to see",
        "<p>Teaching a network to see from scratch takes far more images than we have. Transfer "
        "learning starts from a network trained on over a million everyday photos (a collection "
        "called ImageNet), which already picks up edges, textures and shapes. We then adapt it to "
        "our seven skin lesion categories.</p>",
    ),
    (
        "Why class imbalance matters",
        "Some categories are far more common than others",
        "<p>Of the 10,015 images, 6,705 show melanocytic nevi and only 115 show dermatofibroma. "
        "That uneven mix is called class imbalance. A model can score well overall by favoring the "
        "common category while missing the rare ones, so we look at each category separately and "
        "not only at overall accuracy.</p>",
    ),
    (
        "Where it can fail",
        "Treat every output as a guess",
        "<ul>"
        "<li>Rare categories have few examples to learn from.</li>"
        "<li>Images unlike the training photos, such as other cameras, lighting or skin tones, "
        "may be handled less reliably.</li>"
        "<li>It always picks one of seven categories, even for something outside them.</li>"
        "<li>A high model probability does not mean the prediction is correct, and a heatmap "
        "shows influence, not proof.</li>"
        "</ul>",
    ),
]


def render_story():
    section_heading(
        "Project story",
        "What this project is, and what it is not",
        "Four things worth knowing before you trust, or doubt, a prediction.",
    )
    cards = "".join(
        f'<div class="pp-card"><div class="pp-kicker">{kicker}</div><h3>{title}</h3>{body}</div>'
        for kicker, title, body in CARDS
    )
    st.markdown(f'<div class="pp-story">{cards}</div>', unsafe_allow_html=True)
