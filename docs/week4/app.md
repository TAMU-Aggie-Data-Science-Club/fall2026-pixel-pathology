# Week 4 — Real predictions in the Streamlit app

Related issue: #63. Task branch: `issue-63/real-predictions`.

## Setup and launch

Use standard Windows CPython (rather than MSYS Python), or a Python environment
with compatible PyTorch and torchvision packages. From the repository root:

```bash
python -m pip install -r requirements.txt
python -m pip install torch torchvision
python -m streamlit run app/app.py
```

The second command installs the existing Modeling dependencies from its
[prediction handoff](../week3/checkpoint_and_prediction.md). This task does not
change the shared prediction functions or introduce another preprocessing path.

Obtain Modeling's agreed **BatchNorm-corrected baseline** from the shared folder
linked in that handoff. Put `baseline_resnet50.pt` at:

```text
models/baseline_resnet50.pt
```

The app imports `CHECKPOINT_PATH` from `src/model.py`, loads on CPU, and caches
the loaded model. Replacing the checkpoint with a different modification time
or size reloads it on the next page run. Restart the app if replacing weights
while preserving both attributes. The app never downloads pretrained weights
or trains a model. Keep checkpoints out of GitHub.

Uploads work without local HAM10000 data. To select local samples and look up
their known labels, the current app expects:

```text
data/raw/HAM10000_metadata.csv
data/raw/HAM10000_images_part_1/
data/raw/HAM10000_images_part_2/
```

Keep the original JPG names. If your files follow the older `DATA.md` layout
with an extra `HAM10000/` directory, the existing sample picker will not find
those folders. Extract the archives into the locations above, or use image
upload. The metadata location can be overridden before launch, for example:

```powershell
$env:HAM10000_METADATA_PATH = "data/raw/HAM10000/HAM10000_metadata"
```

This override changes metadata lookup, not image-folder discovery. See the
[Week 2 data instructions](../week2/app.md#data). No raw data is committed.

## Prediction behavior

The page uses `load_model` and `predict_probabilities` from `src/predict.py`.
Modeling applies `ResNet50_Weights.IMAGENET1K_V2.transforms()` through the shared
image loader; random training augmentation is never applied to predictions.

The probability table uses `CLASS_NAMES` from `src/model.py`, in this order:
`akiec, bcc, bkl, df, mel, nv, vasc`. The app's existing readable-name dictionary
only supplies display names. The predicted class is the highest-probability
output. Its model probability and all seven probabilities appear as percentages.

**Known dataset label** is a separate metadata section. It is never used as a
prediction or passed into inference. Uploaded images have no known dataset label.

With no selected image, the page asks for one. With a missing checkpoint or
missing Modeling dependencies, it shows a pending message. An incompatible
checkpoint or unreadable image produces an unavailable message without a result
table. Image viewing, the educational notice, and the pending Grad-CAM section
remain available. Reused upload streams are rewound before displaying them.

## Verification

Run the page regression checks from the repository root:

```bash
python -m unittest discover -s tests -p "test_app_prediction.py" -v
```

Checks completed November 2, 2026, using standard Windows CPython 3.12,
Streamlit 1.66.1 and PyTorch 2.15.0+cpu:

- **Eight page regression tests passed.** They cover no selected image, a
  differing metadata label and prediction, ordered output, checkpoint caching
  and replacement, missing/incompatible checkpoints, missing metadata,
  previously read uploads, unreadable images, and invalid probability outputs.
  Controlled inference outputs in these tests verify UI behavior, not model
  quality.
- **Real checkpoint inference passed.** Used the shared baseline on
  `ISIC_0024306`, the image from Modeling's handoff example. The known metadata
  label was `nv`; the top model output was Melanocytic nevi (`nv`) at
  **83.25%**. Seven probabilities summed to `0.9999999302`. A previously read
  uploaded-file-style stream produced the same probabilities as the file path.
- **Full-page AppTest with real inference passed.** Confirmed the seven rows in
  shared class order, known-label section, original image and educational
  notice. This check supplied the existing local image and metadata paths to
  accommodate the older nested layout; it did not change sample discovery.
- App/test Python syntax parsing and `git diff --check` passed.
- The documented Streamlit launch command started successfully; the local
  server returned HTTP 200 on its health endpoint and was then shut down.

The checked weights were `models/baseline_resnet50.pt`, epoch **10**, with
checkpoint-recorded validation loss **0.9261303494**. SHA-256:

```text
9a20fb9e87d8629d621ce62de738b98fa9803c5fd30a98e13f95e4f725923582
```

To repeat the real inference check with the standard data layout:

```bash
python src/predict.py --image data/raw/HAM10000_images_part_1/ISIC_0024306.jpg
```

The local verification used the same filename under
`data/raw/HAM10000/HAM10000_images_part_1/`. These are single-image integration
checks, not a new performance evaluation or evidence of clinical correctness.

### Independent teammate check

Another member or PM should run the launch command and record their name,
date, checkpoint identity, outcomes, and blockers here or on #63:

| Check | Expected behavior | Teammate result |
| --- | --- | --- |
| Launch without a selected image | Educational notice, selection prompt, pending heatmap | Pending |
| Upload valid JPG/PNG with checkpoint | Image, readable predicted class, top probability, seven-row table | Pending |
| Select HAM10000 sample | Image and known label remain separate from prediction | Pending |
| Temporarily move checkpoint aside and rerun | Missing-checkpoint message, image remains visible, no probabilities | Pending |
| Restore checkpoint and rerun | Real predictions resume | Pending |
| Metadata unavailable | Metadata message; image and inference still work | Pending |
| Unreadable JPG | Friendly error; page remains usable | Pending |

## Limitations and handoff

- Probabilities are model outputs, not calibrated clinical confidence or a
  diagnosis. This is for education and research only.
- No new training, validation comparison, or test-set evaluation is performed by
  this task. The test set remains untouched.
- The validation confusion-matrix display and its checkpoint-linked explanation
  are a separate team task under #63; this contribution covers prediction wiring.
- Grad-CAM remains pending. No heatmap or lesion boundary is generated.
- Independent teammate verification remains pending until a person records it;
  automated checks do not substitute for that requirement.

## Contributions

- **Abhlnaw — real prediction connection:** Connected Modeling's existing model
  loader and prediction functions to the Week 2 page and merged pending states;
  added the readable top class, its probability, and an ordered table of all
  seven probabilities; preserved metadata separation, notices, image viewing,
  and missing-checkpoint behavior. Added checkpoint-aware model caching, upload
  rewind handling, page regression checks, and these setup/handoff instructions.
- Modeling's shared checkpoint, model, class mapping, preprocessing, and
  prediction functions are reused from the merged #41 work; this contribution
  does not claim those implementations.
