# Week 2 — Streamlit app

## Setup

```bash
pip install -r requirements.txt
```

## Data

To pick HAM10000 samples and see their known dataset labels, put the metadata CSV and unzipped images in `data/raw/`:

```text
data/raw/HAM10000_metadata.csv
data/raw/HAM10000_images_part_1/
data/raw/HAM10000_images_part_2/
```

Upload works without the data.

Known-label lookup defaults to `data/raw/HAM10000_metadata.csv`, relative to the
project root. To use another metadata location, set `HAM10000_METADATA_PATH`
before launching the app. Relative paths resolve from the project root; absolute
paths are also supported. For example, in PowerShell:

```powershell
$env:HAM10000_METADATA_PATH = "data/raw/HAM10000/HAM10000_metadata.csv"
```

The page shows the known label for a selected HAM10000 sample under "Known dataset
label". It shows a message instead when the metadata file or image ID is absent, and
uploaded images have no known label.

## Run

```bash
streamlit run app/app.py
```

## Contributions

- **Hiren — image display:** Added `show_image`, which shows an image as
  RGB and gives a friendly error for unreadable files.
- **Abhlnaw — educational notice and pending sections:** Added the educational-use
  notice and the pending prediction and Grad-CAM sections.
- **Kaushik— notice wording:** Fixed the wording of the educational
  disclaimer.
- **Emily — known-label lookup:** Wrote the first version of the dataset
  label lookup from the HAM10000 metadata.
- **Evan — page and label display:** Built the Streamlit page with image upload and
  HAM10000 sample selection, then connected the known-label lookup to the page as
  "Known dataset label", kept separate from model predictions.
- **Abhlnaw — Week 2 catch-up:** Replaced the personal Windows metadata path with
  a configurable project path, removed the hardcoded test lookup and its display
  block, and documented metadata configuration. Known labels come from dataset
  metadata; they are not model predictions.
