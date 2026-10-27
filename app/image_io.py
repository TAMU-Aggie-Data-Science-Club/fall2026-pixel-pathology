import streamlit as st
from PIL import Image


def show_image(source, caption=None):
    """Open an image and display it as RGB.

    `source` can be an uploaded file or a path to a file on disk.
    Returns True if the image was shown. If the file can't be read,
    shows a friendly error and returns False, so the app keeps running.
    """
    try:
        img = Image.open(source)
        img.load()  # forces a full read, so corrupt files fail here
        img = img.convert("RGB")
    except Exception:
        st.error("Couldn't read that file. Please choose a valid image (JPG or PNG).")
        return False
    st.image(img, caption=caption)
    return True