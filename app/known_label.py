import pandas as pd
from pathlib import Path
import streamlit as st

# get values from csv
# get the image id
# get the dx value from the image id
# display the dx label

table = pd.read_csv(r"C:\Users\emily\OneDrive\Desktop\fall2026-pixel-pathology\dataversefiles\HAM10000_metadata")
table = table.set_index("image_id")

def get_dataset_label(filename):
    image_id = Path(filename).stem
    if (image_id in table.index):
        return table.loc[image_id, "dx"]
    else:
        return None

label = get_dataset_label("ISIC_9999999.jpg")

st.subheader("Dataset label")
if label is not None:
    st.write(f"Dataset label is known: {label}")
else:
    st.info("No dataset label avalible for this image")
