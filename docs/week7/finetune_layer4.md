# Fine-tuning ResNet-50's layer4

PM test run, November 18. Validation split only: the test set was not used.

## What changed from `src/training.py`

| | `training.py` (weighted_sampling.pt) | `finetune.py` |
|---|---|---|
| Trainable layers | 7-class head only | ResNet-50's last block (`layer4`) + 7-class head |
| Trainable parameters | 14,343 | 14,979,079 |
| Optimizer | SGD, lr 0.001 | SGD with momentum 0.9: head lr 0.001, layer4 lr 0.0001 |
| Imbalance handling | Weighted sampling, 1/count | Same (`--weighting inverse`) |
| Augmentation, split, epochs | Unchanged | Unchanged (10 epochs) |
| Checkpoint kept | Lowest validation loss | Highest validation macro F1 |
| BatchNorm | Running statistics fixed | Running statistics fixed (all layers) |

The checkpoint is saved in the same format, so `src/predict.py`, the app and Grad-CAM load it unchanged.

## How to run

```bash
python src/data/create_splits.py data/raw/HAM10000_metadata.csv
python src/finetune.py --name finetune_layer4.pt --epochs 10
```

On an RTX 3050 Ti (4 GB), each epoch took about 30 seconds after the first. The script prints validation metrics every epoch and writes `outputs/finetune/<name>/best_val_metrics.json` and `history.json`.

## Validation results (1,519 images)

The best epoch was 9 of 10. Because that epoch was chosen using validation, these numbers are slightly optimistic. The one-time test run gives the final number.

| | weighted_sampling.pt | finetune_layer4.pt |
|---|---:|---:|
| 7-class macro F1 | 0.319 | **0.579** |
| Benign vs. malignant macro F1 | 0.669 | **0.750** |
| Malignant sensitivity (akiec + bcc + mel) | 57.6% | **81.7%** |
| Benign specificity | 81.9% | **81.7%** |

| Class | weighted_sampling.pt recall | finetune_layer4.pt recall |
|---|---:|---:|
| akiec | 45.6% | 66.7% |
| bcc | 50.8% | 73.8% |
| bkl | 22.8% | 57.8% |
| df | 31.6% | 36.8% |
| mel | 35.3% | 65.4% |
| nv | 53.8% | 79.4% |
| vasc | 92.0% | 68.0% |

The weighted_sampling.pt numbers were re-scored on the same machine with `src/evaluation.py`. They give 0.319 against the 0.320 recorded in `docs/week4/` (bkl has one image different), so the two runs are directly comparable.

Fine-tuning also fixes most of the over-prediction of rare classes. weighted_sampling.pt predicted df 167 times and vasc 277 times, and was usually wrong. The fine-tuned model predicts them 22 and 26 times, with precision of 32% and 65%. vasc recall drops from 92% to 68% as a result.

Benign vs. malignant groups mel, bcc and akiec as malignant or pre-cancerous, and nv, bkl, df and vasc as benign. It is computed from the 7-class predictions, not from a separately trained model.

A gentler weighting (`--weighting sqrt`, 1/√count) reached macro F1 0.590 but caught fewer malignant lesions (73.4% sensitivity) and only 3 of 19 df images. The standard weighting is recommended.

Educational use only. Not a diagnostic tool.
