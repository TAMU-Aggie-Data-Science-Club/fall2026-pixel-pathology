from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit

COLUMNS = [
    "image_id",
    "lesion_id",
    "dx",
    "split"
]


def make_splits(meta, seed=42):
    image_ids = meta["image_id"]
    labels = meta["dx"]

    split1 = GroupShuffleSplit(test_size=0.3, random_state=seed)
    train_idx, temp_idx = next(
        split1.split(image_ids, labels, groups=meta["lesion_id"])
    )

    train_ids = image_ids.iloc[train_idx]
    temp_ids = image_ids.iloc[temp_idx]
    temp_labels = labels.iloc[temp_idx]

    split2 = GroupShuffleSplit(test_size=0.5, random_state=seed)
    val_idx, test_idx = next(
        split2.split(
            temp_ids,
            temp_labels,
            groups=meta["lesion_id"].iloc[temp_idx],
        )
    )

    val_ids = temp_ids.iloc[val_idx]
    test_ids = temp_ids.iloc[test_idx]
    return train_ids, val_ids, test_ids


def export_splits(metadata_path, output_path="data/processed/combined_splits.csv", seed=42):
    meta = pd.read_csv(metadata_path)
    train_ids, val_ids, test_ids = make_splits(meta, seed=seed)

    # Just concatenate the splits into a single dataframe with a "split" column
    split_df = pd.concat(
        [
            train_ids.to_frame(name="image_id").assign(split="train"),
            val_ids.to_frame(name="image_id").assign(split="val"),
            test_ids.to_frame(name="image_id").assign(split="test"),
        ],
        ignore_index=True,
    )

    # Merge the split dataframe with the original metadata to include lesion_id and dx
    split_df = split_df.merge(
        meta[["image_id", "lesion_id", "dx"]], on="image_id", how="left"
    )

    split_df = split_df[COLUMNS]

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    split_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create HAM10000 data splits.")
    parser.add_argument("metadata_csv", help="Path to HAM10000 metadata CSV")
    parser.add_argument("--output-path", default="data/processed/splits.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    export_splits(args.metadata_csv, args.output_path, args.seed)
