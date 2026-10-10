# Data — Pixel Pathology

## Selected dataset

We are using **HAM10000** for our first version: a seven-class skin-lesion classification project with transfer learning and Grad-CAM visualizations.

This is an educational project, not a diagnostic tool.

| Field | Details |
|---|---|
| Dataset | HAM10000 |
| Official source | Harvard Dataverse |
| Dataset link | https://doi.org/10.7910/DVN/DBW86T |
| Project snapshot | Version 4.0, downloaded October 9, 2026 |
| Images | 10,015 dermoscopic images |
| Labels | Seven diagnostic categories |
| Access | Download the metadata and image archives from the source page |
| Terms | Read the dataset's Terms tab and record the exact license before publishing dataset images or redistributing data |
| Storage | Local files under `data/`; never commit raw images, archives, or source metadata |

We are starting with this dataset only. Additional datasets require discussion with the PMs.

## Download instructions

### Week 1: metadata only

1. Open the official dataset link above.
2. Find the HAM10000 metadata file.
3. Download the **original comma-separated CSV** version.
4. Save it locally as:

   `data/raw/HAM10000/HAM10000_metadata.csv`

If your download has no file extension, rename it to include `.csv`. Do not download the tab-separated version for this assignment.

### Later: images for training

Download and extract both archives:

- `HAM10000_images_part_1.zip`
- `HAM10000_images_part_2.zip`

Keep the original JPG filenames. Our data loader will search both image folders.

Use this local layout:

```text
data/raw/HAM10000/HAM10000_metadata.csv
data/raw/HAM10000/HAM10000_images_part_1/
data/raw/HAM10000/HAM10000_images_part_2/
```

The image archives are not needed for the Week 1 metadata assignment.

## Metadata columns

| Column | Meaning |
|---|---|
| `image_id` | Image identifier; matches a JPG filename without `.jpg` |
| `lesion_id` | Lesion identifier; multiple images can show the same lesion |
| `dx` | Diagnostic category used as the classification label |
| `dx_type` | Method used to establish the diagnosis |
| `age` | Recorded age; some entries are missing |
| `sex` | Recorded sex; some entries are marked unknown |
| `localization` | Body location of the lesion |
| `dataset` | Source collection identifier in our downloaded metadata |

For the initial model, the input will be an image and the target will be `dx`. We are not initially using demographic columns as model inputs.

## Label distribution

The downloaded metadata contains:

| Label | Category | Image count |
|---|---|---:|
| `nv` | Melanocytic nevi | 6,705 |
| `mel` | Melanoma | 1,113 |
| `bkl` | Benign keratosis-like lesions | 1,099 |
| `bcc` | Basal cell carcinoma | 514 |
| `akiec` | Actinic keratoses and intraepithelial carcinoma | 327 |
| `vasc` | Vascular lesions | 142 |
| `df` | Dermatofibroma | 115 |
| **Total** | | **10,015** |

These are diagnostic categories, not seven types of cancer.

The classes are unevenly represented. Report per-class performance and metrics such as macro F1 and balanced accuracy alongside overall accuracy.

## Initial readiness status

As of October 9, 2026:

- The PM downloaded the metadata and both image archives.
- Both image archives were extracted, and sample images were opened.
- The metadata contains 10,015 rows and 10,015 unique image IDs.
- The metadata contains 7,470 unique lesion IDs.
- There are 57 missing age values.

Still to complete before training:

- Match every metadata image ID to a local image file.
- Check for unreadable images and duplicate image content.
- Record the dataset's exact license and attribution requirements.
- Create and verify the train, validation, and test split manifests.

## Splitting rules

**Split by `lesion_id`, not by individual image.**

Multiple images can show the same lesion. All images with the same `lesion_id` must remain in one split to prevent information leaking between training and evaluation.

The downloaded metadata does not provide a patient ID, so lesion grouping does not guarantee patient separation.

The Data team will:

1. Create reproducible splits using a fixed random seed.
2. Preserve class representation where feasible.
3. Verify that no lesion IDs overlap across splits.
4. Save split manifests and document the method.
5. Apply augmentation and any oversampling only to training data.

The test set stays held out until final evaluation.

## Week 1 assignment

The Data & Analysis team will submit:

`notebooks/week1_data_exploration.ipynb`

The notebook should:

- Load the metadata CSV.
- Explain `image_id`, `lesion_id`, and `dx`.
- Show class counts in a table or chart.
- Include three observations about the data.
- Explain why we must split by lesion ID.
- Include members' contribution summaries and short reflections.

No model training or full image download is required this week.

## Repository rules

Commit code, notebooks, documentation, and aggregate results.

Do not commit downloaded metadata, image archives, raw images, or generated image tensors. Keep these under the git-ignored `data/` folder.

Before committing notebooks, check that they do not embed dataset images or expose personal local file paths.

Any published image examples must follow the dataset's reuse and attribution terms.

## References

- Dataset: https://doi.org/10.7910/DVN/DBW86T
- Original paper: https://doi.org/10.1038/sdata.2018.161t fetches and builds these folders** is what must be committed and reproducible — not the data itself.
