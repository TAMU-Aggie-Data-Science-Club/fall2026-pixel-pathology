# Week 5 — App confusion matrix

Issue: #78. Contribution: Abhlnaw — display the existing confusion matrix with
its model and split clearly identified.

## Run

From the repository root:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app/app.py
```

For the integrated prediction and Grad-CAM flow, also follow the existing
[model dependency and checkpoint setup](../week4/app.md#setup-and-launch) and
[Grad-CAM instructions](gradcam.md).

The **Model performance — Confusion matrix** section appears below the existing
demo sections. It is available without an upload, local dataset or checkpoint.

## Result displayed

- Model: **ResNet-50 baseline — `baseline_resnet50.pt` (BatchNorm-corrected)**.
- Split: **Validation — 1,519 HAM10000 images**.
- Artifact: [`baseline_matrix.png`](../week3/baseline_matrix.png), with provenance
  in [Modeling's evaluation notes](../week3/evaluation.md) and aggregate counts
  in [`baseline_metrics.json`](../week3/baseline_metrics.json).
- Rows are true labels and columns are predicted labels; cells contain counts.

This is an existing validation evaluation, not an evaluation of the uploaded
image or a guarantee about whichever checkpoint is loaded elsewhere in the app.
It is not test-set or clinical performance. No evaluation was rerun, no data or
checkpoint was added. The merged prediction and Grad-CAM implementations are
preserved, with the confusion matrix displayed after those demo sections.

## Verification

Streamlit AppTest passed on November 8, 2026: the saved matrix, model/checkpoint
name, validation split, 1,519-image count, axis explanation and educational
notice appear with no image selected. The display also passed from a different
working directory. The image count matches the sum of the saved matrix counts.
Python syntax parsing and `git diff --check` passed.

On November 11, 2026, merged `issue-63/integration` after #73 and #80 and resolved
`app/app.py` to retain real predictions, Grad-CAM and the labeled matrix. All
15 existing prediction/Grad-CAM tests passed, and the matrix page check passed
again, including from a different working directory. These automated checks do
not replace Hiren's independent Grad-CAM test reported by the PM. Week 6 torch
and data-folder tasks in #84 are outside this change.
