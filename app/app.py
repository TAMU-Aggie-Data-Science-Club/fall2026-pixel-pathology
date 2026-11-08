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
