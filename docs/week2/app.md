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

## Run

```bash
streamlit run app/app.py
```
