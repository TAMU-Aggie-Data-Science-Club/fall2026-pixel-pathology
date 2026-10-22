"""Seven-class HAM10000 classifier built on an ImageNet-pretrained ResNet-50."""

import torch.nn as nn
from torchvision import models

# Class order agreed by PMs on Oct 17 (issues #21-#23). Output index i of the
# model is the logit for CLASS_NAMES[i]. Data splits, the loader and the app
# must all use this same order.
CLASS_NAMES = ["akiec", "bcc", "bkl", "df", "mel", "nv", "vasc"]
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASS_NAMES)}
NUM_CLASSES = len(CLASS_NAMES)


def build_model(num_classes=NUM_CLASSES, pretrained=True):
    """Return a ResNet-50 whose final layer outputs `num_classes` logits.

    The convolutional backbone keeps its ImageNet weights. The original
    1000-class `fc` layer is replaced with a new, randomly initialised
    Linear(2048, num_classes) layer that is learned during training.
    The model returns raw logits; apply softmax to get probabilities.
    """
    weights = models.ResNet50_Weights.IMAGENET1K_V2 if pretrained else None
    model = models.resnet50(weights=weights)
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    return model


if __name__ == "__main__":
    # Shape check only: a random tensor, not real images or an evaluation.
    import torch

    model = build_model()
    model.eval()
    x = torch.randn(2, 3, 224, 224)
    with torch.no_grad():
        logits = model(x)
    print(f"head: {model.fc}")
    print(f"input shape:  {tuple(x.shape)}")
    print(f"output shape: {tuple(logits.shape)}")
    print(f"class order:  {CLASS_NAMES}")
    assert logits.shape == (2, NUM_CLASSES)
