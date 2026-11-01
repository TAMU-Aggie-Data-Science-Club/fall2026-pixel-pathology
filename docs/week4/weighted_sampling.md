# Week 4: Weighted Sampling Evaluation

## Method

Evaluated weighted_sampling.pt on all 1,519 validation images
using the shared ResNet50 IMAGENET1K_V2 preprocessing, without random
augmentation. Test images were not evaluated. (Model was trained for 10 epochs)

Predictions use the highest-scoring class. Macro F1 is calculated over
the entire validation set with equal weight for all seven classes and
zero_division=0.

Class order: akiec, bcc, bkl, df, mel, nv, vasc.

## Results

After weighted sampling, the classification of nv worsened while improvements in the other six lesion classes saw improvement. 23 of the 25 vasc lesions were correctly classified, while the other lesions had more distribution in their respective rows. Compared to the corrected baseline, the F1 score saw an imporvement of ~0.146.

- Validation macro F1: 0.32023200121813994.
- Validation images: 1,519.
- Device: Apple MPS.
- Batch size: 16; shuffle=False; drop_last=False.

Full results: [weighted_sampling_metrics.json](weighted_sampling_metrics.json).

Matrix rows are true labels; columns are predicted labels.

![Weigted sampling confusion matrix](weighted_sampling_matrix.png)