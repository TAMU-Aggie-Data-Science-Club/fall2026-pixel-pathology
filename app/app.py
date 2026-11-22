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
st.markdown("**Model:** ResNet-50, layer3 + layer4 fine-tuned with weighted sampling — `finetune_layer34.pt`")
st.markdown("**Split:** Test — 1,494 HAM10000 images (evaluated once)")
st.image(
    str(Path(__file__).resolve().parent.parent / "docs" / "week7" / "figures" / "confusion_matrix_test.png"),
    caption="finetune_layer34.pt — test split, 1,494 images",
)
st.caption(
    "Rows are true dataset labels; columns are model predictions. "
    "This is the saved test evaluation of finetune_layer34.pt, separate from "
    "the selected image's prediction. It does not report clinical performance."
)
