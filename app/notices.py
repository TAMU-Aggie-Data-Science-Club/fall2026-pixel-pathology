import streamlit as st

from image_io import show_image

# Class order agreed at the Oct 17 sync (alphabetical, matches model output index).
CLASS_NAMES = {
    "akiec": "Actinic keratoses",
    "bcc": "Basal cell carcinoma",
    "bkl": "Benign keratosis",
    "df": "Dermatofibroma",
    "mel": "Melanoma",
    "nv": "Melanocytic nevi",
    "vasc": "Vascular lesions",
}


def show_educational_notice():
    """Show the educational-use notice as a dark banner."""
    st.markdown(
        '<div style="display:flex;background:#1f2023;color:#fff">'
        '<div style="padding:1rem 1.5rem;border-right:1px solid #555;'
        'font-size:0.75rem;font-weight:600;letter-spacing:0.15em">NOTICE</div>'
        '<div style="padding:1rem 1.5rem">'
        "<b>FOR EDUCATIONAL AND DEMONSTRATION PURPOSES ONLY.</b> "
        "This web application is a student learning project created for the "
        "Aggie Data Science Club (ADSC). It is <b>not</b> a clinical diagnostic "
        "tool, medical device, or replacement for professional medical advice, "
        "diagnosis, or treatment. Do <b>not</b> use this as a replacement for a "
        "medical professional, and always seek the advice of a qualified "
        "dermatologist with any questions regarding skin conditions or lesions."
        "</div></div>",
        unsafe_allow_html=True,
    )


def placeholder(text):
    """Show an empty grey box where an image will go."""
    st.markdown(
        '<div style="height:300px;display:flex;align-items:center;justify-content:center;'
        "background:rgba(128,128,128,0.08);border:1px solid rgba(128,128,128,0.3);"
        f'color:gray;font-size:0.8rem;font-weight:600;letter-spacing:0.1em">{text}</div>',
        unsafe_allow_html=True,
    )


def show_pending_outputs(source=None):
    """Keep original-image viewing and the pending Grad-CAM section visible."""
    st.divider()
    st.markdown("#### :gray[Step 3 – Heatmap]")
    st.caption("Pending — a Grad-CAM overlay needs a selected image and the baseline checkpoint. No overlay is available.")
    left, right = st.columns(2)
    with left:
        if source is None or not show_image(source):
            placeholder("NO IMAGE")
        st.caption("Original image")
    with right:
        placeholder("NO IMAGE")
        st.caption("Grad-CAM overlay")
    st.caption(
        "Highlights regions that influenced the prediction. It does not mark "
        "exact lesion boundaries or prove the prediction is correct."
    )
