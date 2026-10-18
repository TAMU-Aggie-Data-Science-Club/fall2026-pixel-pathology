import streamlit as st


def show_educational_notice():
    """Show the Week 1 educational-use notice above the image controls."""
    st.warning(
        "**Disclaimer & Educational Notice**\n\n"
        "**FOR EDUCATIONAL AND DEMONSTRATION PURPOSES ONLY.**\n\n"
        "This web application is a student learning project created for the "
        "Aggie Data Science Club (ADSC). It is **not** a clinical diagnostic "
        "tool, medical device, or replacement for professional medical advice, "
        "diagnosis, or treatment. Do **not** use this as a replacement for a "
        "medical professional, and always seek the advice of a qualified "
        "dermatologist with any questions regarding skin conditions or lesions."
    )


def show_pending_outputs():
    """Show pending sections for future predictions and heatmaps."""
    st.subheader("Prediction — Pending")
    st.info("Model predictions are not implemented yet. No prediction is available.")

    st.subheader("Grad-CAM heatmap — Pending")
    st.info("Heatmap generation is not implemented yet. No Grad-CAM overlay is available.")
