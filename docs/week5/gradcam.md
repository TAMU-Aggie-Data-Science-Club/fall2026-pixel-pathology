# Week 5 — Grad-CAM overlay

Step 3 of the app shows a Grad-CAM heatmap for the model's predicted class, next to the original image. Educational use only, not a diagnosis.

## Setup

Same as the [Week 4 app instructions](../week4/app.md): install the requirements plus `torch` and `torchvision`, and put the baseline checkpoint at `models/baseline_resnet50.pt` (see [checkpoint_and_prediction.md](../week3/checkpoint_and_prediction.md)).

```bash
streamlit run app/app.py
```

Choose an upload or a HAM10000 sample. Step 3 shows the heatmap for whichever class Step 2 predicts. With no image or no checkpoint it stays marked pending.

## How it works

`app/gradcam.py` uses plain PyTorch, with no extra package. It hooks the last convolutional block of ResNet-50 (`layer4[-1]`), weights that block's feature maps by the gradient of the predicted class's score, and blends the result over the 224×224 crop the model sees.

The highlighted regions influenced the model's prediction. They do not mark lesion boundaries and do not establish a diagnosis.

## Checks

`tests/test_gradcam.py` checks the heatmap against a classic CAM computed independently from the final layer's weights, and checks the page with and without a working model. These use an untrained model, so they do not evaluate heatmap quality.

Teammate reproduction: pending.
