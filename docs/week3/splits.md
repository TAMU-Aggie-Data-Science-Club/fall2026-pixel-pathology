# Running Split Creation and Verification

Requires Python, scikit, and pandas. For safety, recommended to try upgrading pip before running these commands. Running without may cause an error.

```
python -m pip install --upgrade pip
pip -m pip install scikit-learn pandas
```

Then run create_splits.py on the raw data. This can be done anywhere in the project folder, but from the upper-most level within fall2026-pixel-pathology:

```
python src/data/create_splits.py data/raw/HAM10000_metadata.csv
```

Once the splits are generated, check `data/processed/` for a `splits.csv`. If it's present, run verification:

```
python src/data/verify_splits.py data/raw/HAM10000_metadata.csv
```

Should produce an output containing class counts in each split and should print that all split checks passed.

```
Class counts per split:
dx     akiec  bcc  bkl  df  mel    nv  vasc
split
train    207  381  741  89  770  4718    96
val       57   65  206  19  156   991    25
test      63   68  152   7  187   996    21
All split checks passed.
```
