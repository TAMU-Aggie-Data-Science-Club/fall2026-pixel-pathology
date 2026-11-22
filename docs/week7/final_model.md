# Final model and test results

Related: #94 (Week 7 Modeling & Experiments). Educational use only. Not a diagnostic tool.

## Final model

**`finetune_layer34.pt`**: ResNet-50 (ImageNet `IMAGENET1K_V2`) with `layer3`, `layer4` and the 7-class head fine-tuned, trained with weighted sampling (weight 1/class count). Download it from the [Releases page](https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-pixel-pathology/releases/tag/model-finetune-layer34-v1). The checkpoint format matches `src/training.py`, so `src/predict.py`, the app and Grad-CAM load it unchanged.

```bash
python src/finetune.py --name finetune_layer34.pt --epochs 15 --unfreeze-layer3
```

| Setting | Value |
|---|---|
| Trainable layers | layer3 + layer4 + head (22,077,447 parameters) |
| Optimizer | SGD with momentum 0.9: head lr 0.001, layer3/layer4 lr 0.0001 |
| Epochs | 15. The epoch with the best validation macro F1 is kept (epoch 15). |
| Augmentation, split, BatchNorm | Same as `src/training.py` (BatchNorm running statistics fixed) |
| Hardware | RTX 3050 Ti, about 30 seconds per epoch |

## How it was chosen (validation only)

Every candidate was compared on the 1,519 validation images. The model was locked before the test set was evaluated.

| Model | 7-class macro F1 | Benign vs. malignant F1 | Malignant sensitivity | Benign specificity |
|---|---:|---:|---:|---:|
| weighted_sampling.pt (head only) | 0.319 | 0.669 | 57.6% | 81.9% |
| layer4, 10 epochs | 0.579 | 0.750 | 81.7% | 81.7% |
| layer4, 1/√count weighting | 0.590 | 0.775 | 73.4% | 87.8% |
| layer4, 20 epochs | 0.632 | 0.788 | 66.5% | 91.8% |
| **layer3 + layer4, 15 epochs** | **0.657** | **0.791** | **84.9%** | 85.3% |

layer3 + layer4 scored best on 7-class macro F1 and caught the most malignant lesions. The 20-epoch layer4 run was close on F1, but its melanoma recall fell to 45%, so it was not chosen.

## Test results (1,494 images, evaluated once)

```bash
python src/evaluation.py --checkpoint models/finetune_layer34.pt --output-dir outputs/test/finetune_layer34 --split test --device cuda
```

| | weighted_sampling.pt | **finetune_layer34.pt (final)** |
|---|---:|---:|
| 7-class macro F1 | 0.335 | **0.644** |
| Benign vs. malignant macro F1 | 0.680 | **0.775** |
| Malignant sensitivity (akiec + bcc + mel) | 58.5% | **78.3%** |
| Benign specificity | 81.5% | **84.4%** |
| Overall accuracy | 51.1% | **77.8%** |

| Class | Test images | weighted_sampling.pt recall | Final recall |
|---|---:|---:|---:|
| akiec | 63 | 50.8% | 63.5% |
| bcc | 68 | 50.0% | 79.4% |
| bkl | 152 | 29.6% | 65.8% |
| df | 7 | 14.3% | 57.1% |
| mel | 187 | 38.0% | 65.8% |
| nv | 996 | 56.5% | 82.9% |
| vasc | 21 | 81.0% | 76.2% |

Test macro F1 (0.644) is close to validation (0.657), so the model generalizes to unseen lesions. weighted_sampling.pt was also scored on test as a fixed comparison. It played no part in choosing the model.

Benign vs. malignant groups mel, bcc and akiec as malignant or pre-cancerous, and nv, bkl, df and vasc as benign. It is computed from the 7-class predictions. `src/evaluation.py` now reports it, and has a `--split test` option.

## Known weaknesses

- **Melanoma is still often called a mole.** 38 of 187 test melanomas (20%) were predicted as nv, and 120 of 996 moles (12%) were predicted as mel.
- **Rare classes are noisy.** The test set has only 7 df and 21 vasc images, so one image moves recall by 5–14 points.
- **Confidence is not calibrated.** The fine-tuned model is often close to 100% confident, even when it's wrong (see figures/gradcam_examples.png).
- **Grad-CAM shows where the model looked, not whether it is right.** In the missed-melanoma example, the heatmap covers the lesion, yet the prediction is wrong.

## Figures

All figures are 300 DPI on white, in [`figures/`](figures/).

- `class_distribution.png`: all 10,015 HAM10000 images by class
- `per_class_recall_test.png`: test recall, head-only model vs. final model
- `confusion_matrix_test.png`: final model on the test set (counts and row percentages)
- `gradcam_examples.png`: Grad-CAM from the final model on three validation images, two correct and one missed melanoma
