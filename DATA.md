# Data

This file explains **Pixel Pathology's** suggested data sources.

> **`DATA.md` is tracked in git. The `data/` folder is not.** Medical imaging datasets are often licensed for research only and must never be committed. Clone the repo, then populate `data/` locally.

## Suggested sources (starting point)

Pick **one** for v1. Each has its own licensing quirks — read them before downloading.

| Source | Origin / URL | Access method | License | Sensitivity | Notes |
|--------|--------------|---------------|---------|-------------|-------|
| ISIC Archive (skin lesions) | https://www.isic-archive.com/ | ISIC-CLI or Kaggle mirror (ISIC 2019 / 2020) | CC-BY-NC — research use | Low (de-identified imagery) | Well-labeled, class-imbalanced. Multi-class melanoma / nevus / etc. |
| APTOS 2019 Blindness Detection | https://www.kaggle.com/competitions/aptos2019-blindness-detection | Kaggle competition download | Competition rules — research use | Low (de-identified retinal scans) | 5-class DR severity. Highly imbalanced. |
| NIH ChestX-ray14 | https://nihcc.app.box.com/v/ChestXray-NIHCC | Direct download | Public / open | Low (de-identified) | Large (~112k images) — slower to iterate, save for later. |
| PadChest | https://bimcv.cipf.es/bimcv-projects/padchest/ | Request access | Non-commercial research | Low | Alternative to ChestX-ray14 with more granular labels. |

## How to think about using each source

- **License first.** Every dataset above is research-only. This project qualifies, but that also means: don't publish the raw images, don't ship a commercial product, and don't post individual example images without confirming per-dataset re-use terms.
- **Framing.** Even though the images are de-identified, treat them as sensitive. Don't post inference results with patient-identifying context. Never overclaim clinical utility in write-ups.
- **Class imbalance.** All three are heavily imbalanced. Accuracy is a bad metric — track AUC, PR-AUC, class-conditional recall.
- **Reproducibility.** Cache the exact snapshot version (some datasets update). Log dataset hashes in the training script.

Choosing and vetting a source is a **judgment call** — surface it to a PM rather than deciding a major data direction alone.

## Local layout convention

```
data/
├── raw/          # dataset as downloaded — never edit by hand
├── interim/      # resized / normalized image tensors, split manifests
└── processed/    # train/val/test splits and label files
```

Because `data/` isn't in git, the **pipeline that fetches and builds these folders** is what must be committed and reproducible — not the data itself.
