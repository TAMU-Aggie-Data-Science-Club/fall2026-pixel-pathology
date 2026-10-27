# Week 3: Baseline checkpoint and prediction functions

Contributor: @sydip
Related issue: #41, tasks 7–8

Code: [`src/training.py`](../../src/training.py) (saving), [`src/predict.py`](../../src/predict.py) (prediction), [`src/model.py`](../../src/model.py) (`CHECKPOINT_PATH`, `CLASS_NAMES`).

## Checkpoint location

Training saves the best-validation checkpoint to:

```text
models/baseline_resnet50.pt
```

- The path is `CHECKPOINT_PATH` in `src/model.py`. Import it rather than retyping the path.
- `models/` is listed in `.gitignore`. Do not commit checkpoints (~95 MB).
- The file is overwritten each time validation loss improves, so after a run it holds the epoch with the lowest validation loss. The test set is not used.

The checkpoint is a dictionary:

| Key | Contents |
|---|---|
| `model_state_dict` | ResNet-50 weights with the seven-class `fc` layer |
| `class_names` | Output class order at training time (`CLASS_NAMES`) |
| `epoch` | Epoch (1-based) of the saved weights |
| `val_loss` | Validation loss of the saved weights |

## Obtaining the checkpoint

A shared download location has not been chosen yet (**TBD — PMs to decide**). Until then, reproduce it locally.

## Reproducing the checkpoint

1. Set up the local data layout from [`DELIVERABLES.md`](../../DELIVERABLES.md) (Week 3 → Shared standards) and generate the split files the training script reads.
2. Install dependencies:

   ```bash
   python -m pip install torch torchvision pandas pillow
   ```

3. From the repository root, run:

   ```bash
   python src/training.py
   ```

   This trains the head for 10 epochs and writes `models/baseline_resnet50.pt`.

## Prediction functions

From `src/predict.py`:

| Function | Input | Returns |
|---|---|---|
| `load_model(checkpoint_path=CHECKPOINT_PATH, device="cpu")` | Checkpoint path, device | Model in eval mode. Raises `FileNotFoundError` if the checkpoint is missing. Raises `ValueError` if its class order differs from `CLASS_NAMES`. |
| `prepare_image(image)` | File path, uploaded file object (e.g. Streamlit upload), or PIL image | Tensor of shape `(1, 3, 224, 224)` |
| `predict_probabilities(model, image)` | Loaded model; same image inputs as `prepare_image` | List of seven floats summing to 1. Index `i` is the probability for `CLASS_NAMES[i]`. |

- `prepare_image` converts to RGB and applies the agreed V2 prediction preprocessing: `transform` from `src/img_loader.py`, `ResNet50_Weights.IMAGENET1K_V2.transforms()`, which resizes to 232, center-crops to 224, and normalizes with ImageNet mean/std. Random augmentation is not applied.
- Uploaded file objects are rewound before reading, so the app can display an upload and then predict on it.
- Load the model once and reuse it for every prediction.

Example (modules in `src/` import each other by bare name, so `src/` must be on `sys.path`):

```python
import sys
sys.path.insert(0, "src")

from model import CLASS_NAMES
from predict import load_model, predict_probabilities

try:
    model = load_model()
except FileNotFoundError:
    model = None  # show a "prediction pending" message and keep image viewing working

if model is not None:
    probs = predict_probabilities(model, "path/to/image.jpg")
    top = max(range(len(CLASS_NAMES)), key=probs.__getitem__)
    print(CLASS_NAMES[top], probs[top])
```

Command-line check on one image:

```bash
python src/predict.py --image data/raw/HAM10000_images_part_1/ISIC_0024306.jpg
```

This prints the seven probabilities as JSON, keyed by class name in `CLASS_NAMES` order.

## Verification

Checked with a short training run on synthetic stand-in images (no real data was available locally). This confirms the save and load path, not model quality:

- `train_model()` saved `models/baseline_resnet50.pt`, and `git status` shows it ignored.
- `load_model()` returned an eval-mode model whose `fc` weights match the checkpoint.
- `prepare_image` returned `(1, 3, 224, 224)`. A path, an already-read uploaded-file-style object, and a grayscale PIL image all produced seven probabilities summing to 1.
- A missing checkpoint raised `FileNotFoundError`. A checkpoint with a different class order raised `ValueError`.

**Still to do:** run `src/predict.py` on a real HAM10000 image with the real baseline checkpoint and record the output here.

This is an educational project, not a diagnostic tool.
