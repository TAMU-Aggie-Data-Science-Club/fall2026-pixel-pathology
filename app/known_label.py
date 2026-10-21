from pathlib import Path

import pandas as pd
import streamlit as st

from notices import CLASS_NAMES

METADATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "HAM10000_metadata.csv"


@st.cache_data
def load_labels():
    """Return {image_id: dx} from the HAM10000 metadata, or None if the CSV is missing."""
    if not METADATA_PATH.exists():
        return None
    table = pd.read_csv(METADATA_PATH)
    return dict(zip(table["image_id"], table["dx"]))


def get_dataset_label(image_id):
    """Return the dx code for image_id, or None if it isn't in the metadata."""
    labels = load_labels()
    if labels is None:
        return None
    return labels.get(image_id)


def show_known_label(source, image_id):
    """Show the sample's known dataset label, kept separate from model predictions."""
    if source is None:
        return
    st.markdown("##### Known dataset label")
    if image_id is None:
        st.caption("Uploaded images have no known dataset label.")
        return
    if load_labels() is None:
        st.info("HAM10000 metadata not found. Put it at data/raw/HAM10000_metadata.csv.")
        return
    label = get_dataset_label(image_id)
    if label is None:
        st.info("No dataset label available for this image.")
        return
    st.markdown(f"{label} — {CLASS_NAMES.get(label, label)}")
    st.caption("From HAM10000 metadata. This is not a model prediction.")
