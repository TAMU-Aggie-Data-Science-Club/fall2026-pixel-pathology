# Week 2 Final Documentation

**Documentation: Melanie Chappetta**

## Overview

This document summarizes the HAM10000 metadata audit, image audit, lesion-grouped splits, and verification results from `Week2_data_analysis.ipynb`. Results below are taken from the notebook's saved outputs.

## Related Resources

- Week 2 requirements and approved class mapping: repository issue #21.
- [Project deliverables](../../DELIVERABLES.md)
- [Contribution guidelines](../../CONTRIBUTING.md)
- Notebook: `Week2_data_analysis.ipynb`. Its repository location is pending confirmation.

## Member Contributions

| Member | Assigned contribution |
|---|---|
| Devyani Lenin | Metadata audit |
| Rishita Singh | Image audit |
| Parin Vakati | Split generation |
| Yaden Gant | Split verification |
| Melanie Chappetta | Final documentation and coordination |

## Environment and Dependencies

The notebook runs in Google Colab and accesses the dataset through Google Drive.

Required packages:

- pandas
- scikit-learn
- Pillow

The notebook also uses Python's built-in os and pathlib modules, Google Colab's Drive integration, and the unzip command.

If packages are missing, run this in a Colab code cell:

    %pip install pandas scikit-learn Pillow

Package versions are not recorded in the notebook.

## Data Paths

### Metadata CSV

`/content/drive/MyDrive/PixelPathologyFall2026/data/raw/HAM10000/HAM10000_metadata.csv`

### Image Archives

- `/content/drive/MyDrive/PixelPathologyFall2026/data/Image_Data/HAM10000_images_part_1.zip`
- `/content/drive/MyDrive/PixelPathologyFall2026/data/Image_Data/HAM10000_images_part_2.zip`

### Extracted Image Folders

- `/content/images_part_1`
- `/content/images_part_2`

If the shared project folder cannot be accessed through My Drive, add a shortcut to `PixelPathologyFall2026` in My Drive.

## How to Run

Open `Week2_data_analysis.ipynb` in Google Colab and run the cells from top to bottom:

1. Mount Google Drive and extract both image archives.
2. Load the metadata CSV.
3. Run the metadata audit cells.
4. Run the image audit cell.
5. Run the split-generation cell.
6. Run the split-verification cell.

Later cells depend on variables created earlier.

The notebook uses these commands to create the local image folders and extract the archives:

    !mkdir -p /content/images_part_1
    !mkdir -p /content/images_part_2
    !unzip -q "/content/drive/MyDrive/PixelPathologyFall2026/data/Image_Data/HAM10000_images_part_1.zip" -d /content/images_part_1
    !unzip -q "/content/drive/MyDrive/PixelPathologyFall2026/data/Image_Data/HAM10000_images_part_2.zip" -d /content/images_part_2

The current extraction commands may ask whether to replace files when the images already exist.

## Metadata Audit Findings

The metadata contains 10,015 records and 8 columns.

| Check | Saved result |
|---|---:|
| Missing age values | 57 |
| Duplicate image IDs | 0 |
| Records missing image_id, lesion_id, or dx | 0 |
| sex values recorded as "unknown" | 57 |
| localization values recorded as "unknown" | 234 |
| "unknown" values in image_id, lesion_id, or dx | 0 |

The "unknown" strings are separate from null values counted by the missing-value checks.

The 57 records with missing ages were retained because their required identifiers and diagnosis labels are present. No age imputation or record removal is performed by the metadata audit. The original metadata CSV is not modified.

## Image Audit Findings

The image audit searches both extracted folders for `.jpg` files and matches them to the metadata. It opens each located image and uses Pillow's `Image.verify()` to check integrity.

| Check | Saved result |
|---|---:|
| Unique image IDs found across both folders | 10,015 |
| Images passing the integrity check | 10,015 |
| Missing images reported | 0 |
| Corrupt images reported | 0 |

The integrity check does not fully decode each image's pixel data.

The audit records:

- image_id
- lesion_id
- dx
- found_path
- audit_status
- error_details

Missing or corrupt images are flagged and returned separately for review. Only valid records are included in the exported audit table.

The current export path is:

`/content/drive/MyDrive/PixelPathologyFall2026/data/raw/HAM10000/cleaned_HAM10000_metadata.csv`

Despite its filename, this output is a valid-image audit table. It does not preserve all original metadata columns. Writing this separate output does not modify the source metadata CSV or image files.

Split generation currently uses the original metadata. If image problems are found in a future run, they will need to be addressed before generating the final splits.

## Approved Seven-Class Mapping

The decision recorded in issue #21 states that the project managers agreed on this class order on October 17.

| Index | Label | Class name |
|---|---|---|
| 0 | akiec | Actinic keratoses and intraepithelial carcinoma |
| 1 | bcc | Basal cell carcinoma |
| 2 | bkl | Benign keratosis-like lesions |
| 3 | df | Dermatofibroma |
| 4 | mel | Melanoma |
| 5 | nv | Melanocytic nevi |
| 6 | vasc | Vascular lesions |

The data splits, model outputs, and app must use this order. The current notebook uses the string diagnosis codes directly and does not create numeric class-index columns.

## Split Generation

The `make_splits` function uses `GroupShuffleSplit` with random seed 42.

The first split assigns approximately 70% of lesion groups to training and reserves 30% for validation and testing. The second divides the remaining lesion groups approximately equally between validation and testing.

Target proportions:

- Training: 70%
- Validation: 15%
- Testing: 15%

These targets apply to lesion groups, so the image percentages can differ.

Images sharing a `lesion_id` remain together. This prevents images of the same lesion from appearing in both training and evaluation data. The grouping identifier is `lesion_id`, not a patient identifier or diagnosis category.

`GroupShuffleSplit` does not enforce class stratification.

## Split Verification Results

The verification code checks that:

- Every metadata image appears exactly once across the splits.
- No extra images are included.
- No lesion identifiers are missing after matching.
- No `lesion_id` appears in multiple splits.
- Repeating the split function with the same seed produces identical assignments.
- The existing notebook assignments match the function's output using seed 42.

All checks passed in the saved notebook output.

### Image Counts by Class

| Split | akiec | bcc | bkl | df | mel | nv | vasc | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Train | 207 | 381 | 741 | 89 | 770 | 4718 | 96 | 7002 |
| Validation | 57 | 65 | 206 | 19 | 156 | 991 | 25 | 1519 |
| Test | 63 | 68 | 152 | 7 | 187 | 996 | 21 | 1494 |
| Total | 327 | 514 | 1099 | 115 | 1113 | 6705 | 142 | 10015 |

The nv class is the largest class in every split. Class proportions vary between splits because the method groups lesions without enforcing stratification.

## Manifest Status

The verification code creates an in-memory table containing:

| Column | Meaning |
|---|---|
| image_id | Image identifier |
| split | train, val, or test assignment |
| lesion_id | Identifier used to keep images of the same lesion together |
| dx | Diagnosis code |

The notebook does not currently export train, validation, and test manifest files.

Issue #21 specifies that generated manifests should remain local under `data/processed/`. Raw data and generated datasets should not be committed.

The final manifest columns, filenames, and image-path conventions still need to be confirmed and documented.

## Coordination Notes

### Confirmed Decision

The project managers approved the seven-class label-to-index mapping on October 17, as recorded in issue #21. Data splits, model outputs, and the app must use that mapping.

### Pending Confirmation

| Team | Item to confirm | Status |
|---|---|---|
| Modeling & Experiments | Acceptance of the implemented 70/15/15 lesion-group split | Pending |
| Modeling & Experiments | Manifest columns, filenames, and image-path conventions | Pending |
| Explainability & App | Access to sample images and lookup information | Pending |
| Explainability & App | Use of the approved mapping and readable class names | Pending |

Update these entries with the decision and confirmation date after coordination is complete.

## Repository Organization

Issue #21 specifies:

- Audit and split code: `src/data/`
- Exploration notebooks: `notebooks/`
- Findings and run instructions: `docs/week2/`
- Generated manifests: local files under `data/processed/`

Task branches should start from the issue's integration branch, and PRs should target that integration branch.

## Remaining Items

- Confirm acceptance of the implemented 70/15/15 lesion-group split.
- Confirm manifest columns, filenames, and image-path conventions.
- Export the split manifests locally under `data/processed/`.
- Confirm sample access and class-name display with Explainability & App.
- Move the generated audit output outside `data/raw/` to keep generated outputs separate from raw data.
- Confirm that audit and split code is available under `src/data/`.
- Confirm the notebook's repository location and add a direct link.
- Ensure notebook sections and PR descriptions clearly identify each member's contributions.
- Review `DELIVERABLES.md` and update this documentation with any additional requirements.
