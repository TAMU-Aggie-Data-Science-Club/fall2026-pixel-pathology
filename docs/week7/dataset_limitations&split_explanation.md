## Dataset Splitting

The HAM10000 dataset (10,015 images) was divided into training (7,002 images; 69.9%), validation (1,519 images; 15.2%), and testing (1,494 images; 14.9%) sets 
using a group-based splitting approach. `GroupShuffleSplit` was applied with a fixed random seed of 42, ensuring that images from the same lesion remained within 
a single split to prevent lesion-level data leakage. Split verification confirmed no overlapping lesion IDs and reproducible assignments. Class distributions were 
examined across all three subsets to identify potential imbalances.

## Data Limitations

1. **Class Imbalance:** Melanocytic nevi (nv) represent approximately 67% of the dataset, while dermatofibroma (df) and vascular lesions (vasc) are significantly
2. underrepresented. This may bias model predictions toward the majority class.

3. **Missing Demographic Data:** Age information is missing for 57 records, potentially limiting demographic analysis and evaluation across age groups.

4. **Incomplete Metadata:** The dataset contains 57 records with unknown sex and 234 records with unknown lesion localization, limiting subgroup analysis.

5. **Uneven Class Distribution Across Splits:** Although lesion-level separation prevents data leakage, minority-class representation varies across training,
6. validation, and testing sets. For example, dermatofibroma has only 7 test images, reducing the reliability of class-specific performance estimates.
