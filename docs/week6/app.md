# Week 6 — Final checkpoint and matching confusion matrix

Issue #84. Contributor: Abhlnaw — switch the demo to Modeling's final checkpoint
and its matching validation confusion matrix.

## Setup

From the repository root, in the existing app/Modeling Python environment:

```bash
python -m pip install -r requirements.txt
python -m pip install torch torchvision
python -m streamlit run app/app.py
```

Download the exact **weighted_sampling.pt** file recommended by Modeling in
its [weighted-sampling handoff](https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-pixel-pathology/blob/main/docs/week4/weighted_sampling.md#app-handoff)
from the [shared checkpoint folder](https://drive.google.com/drive/folders/1cHydYMl7UWaCWTJKq-wWhFXRHmJ_Jc8R).
Store it locally as:

```text
models/weighted_sampling.pt
```

Do not rename a baseline checkpoint to this filename. Do not commit weights.
Image and metadata setup is unchanged; see the existing
[app data instructions](../week4/app.md#setup-and-launch).

## Model and evaluation displayed

Prediction and Grad-CAM both use `DEMO_CHECKPOINT_PATH` in `app/prediction.py`
and pass that path explicitly to Modeling's shared model loader. The baseline
training and command-line defaults in `src/model.py` are unchanged. There is
no automatic fallback to baseline weights when the final checkpoint is absent.

The page labels the model **ResNet-50 with weighted sampling — weighted_sampling.pt**.
It displays [`docs/week4/weighted_sampling_matrix.png`](../week4/weighted_sampling_matrix.png),
copied unchanged from the published Modeling evaluation. The split is
**validation, 1,519 HAM10000 images**. Rows are true labels, columns are predicted
labels, and cells contain image counts. This saved evaluation is separate from
the selected image's prediction and does not report test-set performance.

The shared seven-class order and IMAGENET1K_V2 prediction preprocessing are
unchanged. Known metadata labels remain separate from predictions. The
educational notice, original-image viewer and missing-checkpoint messages remain
available. Missing weighted weights produce a pending prediction/heatmap rather
than a baseline result mislabeled as weighted sampling.

## Verification

```bash
python -m unittest discover -s tests -v
python src/predict.py --checkpoint models/weighted_sampling.pt --image data/raw/HAM10000_images_part_1/ISIC_0024306.jpg
```

Verified November 14, 2026:

- All **16 prediction/Grad-CAM regression tests passed**. Checks include both
  flows sharing the explicit weighted path, the matrix labels, and missing
  weighted weights remaining pending even if baseline weights are available.
- Real inference on `ISIC_0024306` produced `nv` at **32.86%**. Seven
  probabilities summed to `0.9999999516`; a previously read upload produced
  the same probabilities as the file path.
- Real Grad-CAM produced a finite **224×224** heatmap in the range **0–1** for
  that predicted class. The full-page check displayed the overlay and matching
  matrix, and confirmed that prediction and Grad-CAM loaded the weighted file
  once through the shared cache.
- The matrix's Git blob matches the published artifact on `main` exactly.
  App/test syntax parsing and `git diff --check` passed.

The checked checkpoint records epoch **9**, validation loss **1.4395193035**,
and SHA-256:

```text
a77cee14c7c19292fe93ad2164888ebaff7723ac59da5511c341d6fe35d82bc9
```

The local integration check used the same sample filename under the older
`data/raw/HAM10000/` layout, supplying its existing image and metadata paths to
the page. It did not change data-folder discovery. These single-image checks
are integration evidence, not a new model evaluation or an independent
teammate reproduction.

This contribution does not retrain or reevaluate either model and does not use
the held-out test set. It does not address the separate dependency/data-folder
cleanup, README rewrite or example-screenshot tasks in #84.
