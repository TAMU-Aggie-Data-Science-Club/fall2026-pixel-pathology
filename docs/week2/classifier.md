# Week 2 — Seven-class classifier (ResNet-50)

Part of issue #22 (Modeling & Experiments). Code: [`src/model.py`](../../src/model.py).

Contributor: @sydip — model choice and adapting the classifier to seven outputs.

## Model choice

We use **ResNet-50** pretrained on ImageNet (torchvision `ResNet50_Weights.IMAGENET1K_V2`).

- The project README suggests it as a starting point, and it is widely documented, which makes it easier to debug and explain.
- ImageNet pretraining provides general image features (edges, textures, colour patterns) that transfer to dermoscopic images, so we do not have to learn them from 10,015 images.
- Grad-CAM on ResNet is straightforward: the usual target layer is `model.layer4`.
- It expects 224×224 RGB inputs normalized with ImageNet mean/std, which matches our preprocessing.

## Adapting the classifier to seven outputs

ResNet-50 ends in `fc = Linear(2048, 1000)`, which outputs one score per ImageNet class. `build_model()` replaces it with a new `Linear(2048, 7)` layer:

```python
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V2)
model.fc = nn.Linear(model.fc.in_features, 7)
```

- The convolutional backbone keeps its pretrained weights. Only the new `fc` layer starts from random weights.
- The model outputs **raw logits** of shape `(batch, 7)`. Use `nn.CrossEntropyLoss` on the logits during training. Use `torch.softmax(logits, dim=1)` to get probabilities for predictions.
- No layers are frozen yet. The frozen-backbone baseline is planned for Week 3.

## Output class order

Output index `i` is the score for `CLASS_NAMES[i]`. This order was agreed by the PMs on Oct 17 and is shared by the data splits, the loader and the app:

| Index | Label | Name |
|---:|---|---|
| 0 | `akiec` | Actinic keratoses and intraepithelial carcinoma |
| 1 | `bcc` | Basal cell carcinoma |
| 2 | `bkl` | Benign keratosis-like lesions |
| 3 | `df` | Dermatofibroma |
| 4 | `mel` | Melanoma |
| 5 | `nv` | Melanocytic nevi |
| 6 | `vasc` | Vascular lesions |

Import `CLASS_NAMES` / `CLASS_TO_IDX` from `src/model.py` rather than retyping the order.

## Setup and shape check

Requires `torch` and `torchvision`. From the repo root:

```sh
python -m venv .venv
.venv\Scripts\activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install torch torchvision
python -m src.model
```

The first run downloads the ResNet-50 weights (~100 MB) to the PyTorch cache, outside the repo.

`python -m src.model` passes a random `(2, 3, 224, 224)` tensor through the model to check shapes. It is not a training step or an evaluation. Output:

```text
head: Linear(in_features=2048, out_features=7, bias=True)
input shape:  (2, 3, 224, 224)
output shape: (2, 7)
class order:  ['akiec', 'bcc', 'bkl', 'df', 'mel', 'nv', 'vasc']
```

The training step on real images is a separate task in issue #22.

This is an educational project, not a diagnostic tool.
