import streamlit as st

from known_label import show_known_label
from notices import show_educational_notice, show_pending_outputs
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

show_pending_outputs(source)
