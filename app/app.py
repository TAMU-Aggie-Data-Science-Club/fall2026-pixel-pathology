from pathlib import Path

import streamlit as st

from known_label import show_known_label
from gradcam import show_gradcam
from notices import CLASS_NAMES, show_educational_notice
from prediction import show_prediction
from sample_input import choose_image

# Dashed upload box, as in the demo sketch.
st.markdown(
    "<style>[data-testid='stFileUploaderDropzone']"
    "{border:1px dashed #bbb;border-radius:0}</style>",
    unsafe_allow_html=True,
)

st.title("Pixel Pathology Demo")
show_educational_notice()

st.divider()
st.markdown("#### Step 1 – Upload")
source, image_id = choose_image()
show_known_label(source, image_id)

show_prediction(source, CLASS_NAMES)
show_gradcam(source, CLASS_NAMES)

st.divider()
st.subheader("Model performance — Confusion matrix")
st.markdown("**Model:** ResNet-50 with weighted sampling — `weighted_sampling.pt`")
st.markdown("**Split:** Validation — 1,519 HAM10000 images")
st.image(
    str(Path(__file__).resolve().parent.parent / "docs" / "week4" / "weighted_sampling_matrix.png"),
    caption="ResNet-50 with weighted sampling (weighted_sampling.pt) — validation split, 1,519 images",
)
st.caption(
    "Rows are true dataset labels; columns are model predictions. Values are image counts. "
    "This is the saved validation evaluation of weighted_sampling.pt, separate from "
    "the selected image's prediction. It does not report test-set or clinical performance."
)
