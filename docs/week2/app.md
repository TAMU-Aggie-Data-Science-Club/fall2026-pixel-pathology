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

The lookup returns no label when the metadata file or image ID is absent.
Connecting the lookup to the page is tracked separately on `issue-23/wire-known-label`.

## Run

```bash
streamlit run app/app.py
```

## Contributions

- **Abhlnaw — Week 2 catch-up:** Replaced the personal Windows metadata path with
  a configurable project path, removed the hardcoded test lookup and its display
  block, and documented metadata configuration. Known labels come from dataset
  metadata; they are not model predictions.
