import pandas as pd

from create_splits import make_splits 


def verify_splits(metadata_path, splits_path, seed=42):
    meta = pd.read_csv(metadata_path)
    splits = pd.read_csv(splits_path)

    # Verify that the splits cover all images in the metadata
    assert set(splits["image_id"]) == set(meta["image_id"]), "Splits do not cover exactly the images in the metadata"

    # No lesions appear in multiple splits
    assert splits.groupby("lesion_id")["split"].nunique().le(1).all(), "Lesions appear in multiple splits"

    # Class counts per split
    counts = pd.crosstab(splits["split"], splits["dx"])
    counts = counts.reindex(["train", "val", "test"])
    print("Class counts per split:")
    print(counts)

    # No duplicates
    assert splits["image_id"].is_unique, "Duplicate image_ids in splits file"

    # Same seed same splits
    tr, va, te = make_splits(meta, seed=seed)
    expected = pd.concat([
        pd.DataFrame({"image_id": tr, "split": "train"}),
        pd.DataFrame({"image_id": va, "split": "val"}),
        pd.DataFrame({"image_id": te, "split": "test"}),
    ]).set_index("image_id")["split"]
    actual = splits.set_index("image_id")["split"]
    assert expected.sort_index().equals(actual.sort_index()), \
        "Splits differ from a fresh run with the same seed"

    print("All split checks passed.\n")


# Run on data/raw as it needs to compare when doing make_split verification
if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="Verify HAM10000 data splits.")
    p.add_argument("metadata_csv")
    p.add_argument("--splits-csv", default="data/processed/splits.csv")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    verify_splits(args.metadata_csv, args.splits_csv, args.seed)