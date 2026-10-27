from pathlib import Path

import pandas as pd
from sklearn.model_selection import GroupShuffleSplit


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


def export_splits(metadata_path, output_dir="data/processed", seed=42):
    meta = pd.read_csv(metadata_path)
    train_ids, val_ids, test_ids = make_splits(meta, seed=seed)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    split_ids = {
        "train": train_ids,
        "validation": val_ids,
        "test": test_ids,
    }
    for split_name, image_ids in split_ids.items():
        image_ids.to_frame(name="image_id").to_csv(
            output_path / f"{split_name}.csv", index=False
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create HAM10000 data splits.")
    parser.add_argument("metadata_csv", help="Path to HAM10000 metadata CSV")
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    export_splits(args.metadata_csv, args.output_dir, args.seed)
