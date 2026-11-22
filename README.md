# Pixel Pathology — Intermediate

*ADSC Catalyst Project · Fall 2026*

## Overview

Pixel Pathology trains a neural network to spot disease in medical images — skin lesions, retinal scans, or chest X-rays — and then makes it show its work with Grad-CAM heatmaps that highlight exactly what it noticed. The final artifact isn't "cancer: yes/no" — it's "here's the exact patch the model found worrying."

## Objective

Fine-tune a modern CNN on a real medical-imaging dataset with proper transfer learning, and pair every prediction with an interpretable Grad-CAM overlay in a small demo app.

## Suggested tech stack

- **Data processing:** Python, OpenCV, Pillow
- **Modeling:** PyTorch (or TensorFlow) — CNN with transfer learning (ResNet50, EfficientNet-B0)
- **Interpretability:** Grad-CAM heatmap overlays
- **Visualization / demo:** Streamlit, Matplotlib
- **Data sources:** Kaggle (ISIC skin cancer, APTOS retinopathy, NIH ChestX-ray14)

See [`DATA.md`](DATA.md) for concrete data sources and how to access them.

## What team members will gain

- A model that diagnoses **and** explains itself — rare even in industry
- Transfer-learning skills that show up in every computer-vision job posting
- A project that could genuinely matter to someone's health

## Suggested scope (v1)

Pick **one** dataset. ISIC skin cancer or APTOS retinopathy are both smaller and more tractable than ChestX-ray14 for a semester timeline.

Build:

1. Data loader with proper class-balanced sampling and light augmentation,
2. Transfer-learn ResNet50 or EfficientNet-B0 with a two-stage training recipe (head-only, then fine-tune),
3. Robust evaluation: class-conditional accuracy, ROC/PR curves, calibration,
4. Grad-CAM overlays generated per prediction and displayed in a Streamlit upload demo,
5. A short evaluation writeup with failure-mode examples.

**Out of scope for v1:** clinical validation, multi-dataset transfer, segmentation (this is classification + attribution), federated learning.

**Important framing:** this is a learning project. It is **not** a diagnostic tool. Every artifact and the demo must be labeled as such.

See [`DELIVERABLES.md`](DELIVERABLES.md) for the suggested deliverable breakdown and rough timeline.

## Running the demo

Run these commands from the repository root (the folder containing this README).
Use Python 3.10 or newer with compatible PyTorch/torchvision wheels.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app/app.py
```

On Windows, activate with `.venv\Scripts\activate` instead. If you already have
an environment, activate it and install the requirements; do not recreate it.
Streamlit 1.51 or newer is required for the animated walkthrough. The dark theme
loads from `.streamlit/config.toml` when launched from the repository root.

Download **weighted_sampling.pt** from the team's
[shared checkpoint folder](https://drive.google.com/drive/folders/1cHydYMl7UWaCWTJKq-wWhFXRHmJ_Jc8R)
and place it at `models/weighted_sampling.pt`. Do not rename baseline weights or
commit checkpoints. The documented weighted checkpoint SHA-256 is:

```text
a77cee14c7c19292fe93ad2164888ebaff7723ac59da5511c341d6fe35d82bc9
```

See [the checkpoint handoff](docs/week6/app.md) for provenance. The app uses this
weighted checkpoint for both predictions and Grad-CAM, without a baseline fallback.
Its saved confusion matrix describes **validation, 1,519 images**; a separate line
checks the local checkpoint hash before identifying those results as a match.

You can upload a JPG/PNG without downloading the full dataset. To enable the sample
picker and known labels, use either supported layout:

```text
data/raw/HAM10000_metadata.csv
data/raw/HAM10000_images_part_1/
data/raw/HAM10000_images_part_2/
```

The same three items may instead live inside `data/raw/HAM10000/`. An optional
`HAM10000_METADATA_PATH` environment variable can point to a different metadata CSV.
Images and metadata stay local. See [DATA.md](DATA.md) for source and reuse terms.

The dashboard shows real model outputs. The walkthrough replays those outputs;
the network sketch is labeled conceptual and is not a view of internal activations.
This is an educational project, not a diagnostic tool.

To run the regression checks:

```bash
python -m unittest discover -s tests -v
```

## Repository map

| File / folder | Purpose |
|---|---|
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | **Start here.** How the team runs the project on GitHub — PM vs. member roles, the issue → PR → `main` flow, branching, worktrees, reviews. |
| [`DELIVERABLES.md`](DELIVERABLES.md) | Suggested deliverables and rough timeline. A living plan, not a contract. |
| [`DATA.md`](DATA.md) | Suggested data sources, how to access them, and the source register. |
| [`data/`](data/) | Local working folder for datasets. **Git-ignored** — data is never committed. |
| [`AGENTS.md`](AGENTS.md) | Machine-facing workflow rules for AI coding agents. |
| [`CODEOWNERS`](CODEOWNERS) | **Team roster + review policy.** PMs, members, and the code-owner rule for PRs into `main`. |


## Team

The current PMs and members for this project are listed in [`CODEOWNERS`](CODEOWNERS). PMs listed there are the code owners for PRs into `main`.
## Notes for PMs

This README, [`DELIVERABLES.md`](DELIVERABLES.md), and [`DATA.md`](DATA.md) are **suggestions**, not commitments. Rewrite them as the team scopes the real project.

## Notes for members

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) before touching code. Then pick up an issue from the board.
