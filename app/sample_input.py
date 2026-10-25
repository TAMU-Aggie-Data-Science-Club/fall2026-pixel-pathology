from pathlib import Path

import streamlit as st

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


@st.cache_data
def find_samples():
    """Return {image_id: path} for every local HAM10000 image."""
    paths = sorted(RAW_DIR.glob("HAM10000_images_part_*/*.jpg"))
    return {p.stem: str(p) for p in paths}


def choose_image():
    """Upload an image or pick a HAM10000 sample.

    Returns (source, image_id). source is the uploaded file or sample path,
    or None if nothing is chosen. image_id is only set for samples, so their
    dataset label can be looked up.
    """
    mode = st.radio("Image source", ["Upload", "HAM10000 sample"], horizontal=True)

    if mode == "Upload":
        file = st.file_uploader("Upload a skin lesion image (JPG or PNG)", type=["jpg", "jpeg", "png"])
        if file is None:
            st.caption("No image uploaded yet.")
        return file, None

    samples = find_samples()
    if not samples:
        st.info("No HAM10000 images found. Unzip them into data/raw/HAM10000_images_part_1/ and _part_2/.")
        return None, None

    image_id = st.selectbox("Sample", list(samples))
    return samples[image_id], image_id
