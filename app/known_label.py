import os
from pathlib import Path

import pandas as pd

METADATA_PATH = Path(os.environ.get("HAM10000_METADATA_PATH", "data/raw/HAM10000_metadata.csv")).expanduser()
if not METADATA_PATH.is_absolute():
    METADATA_PATH = Path(__file__).resolve().parent.parent / METADATA_PATH


def get_dataset_label(filename):
    """Return the image's known dx label, or None if metadata or its ID is absent."""
    if not METADATA_PATH.is_file():
        return None

    table = pd.read_csv(METADATA_PATH).set_index("image_id")
    image_id = Path(filename).stem
    if image_id in table.index:
        return table.loc[image_id, "dx"]
    return None
