# Week 2: One training-step check

Contributor: Rahul Bathala (@rahulbathala)
Related issue: #22, tasks 6–7

## What I did

Connected the team's image loader, training augmentation, and seven-class ResNet50. Ran a forward pass, calculated cross-entropy loss, performed backpropagation, and completed one SGD optimizer step.

Used a temporary batch of four real HAM10000 images, as approved by the PM while split manifests are pending. This was a connectivity check, not model evaluation.

## Setup and run

Requires Python, torch, torchvision, pandas, and pillow:

```bash
python -m pip install torch torchvision pandas pillow
```

Run from the repository root, with the team's model.py, img_loader.py, and augmentation.py available under src/:

```bash
python src/training_step.py \
  --manifest "/path/to/HAM10000_metadata" \
  --image-dir1 "/path/to/HAM10000_images_part_1" \
  --image-dir2 "/path/to/HAM10000_images_part_2" \
  --batch-size 4 \
  --temporary-batch
```

Replace the paths with the local metadata file and extracted image folders.

## Actual results

- Device: CPU
- PyTorch: 2.14.1
- Input shape: (4, 3, 224, 224)
- Label shape: (4,)
- Output shape: (4, 7)
- Cross-entropy loss before update: 2.0136656761169434
- Loss finite: yes
- Gradients finite: yes
- Optimizer steps completed: 1
- Maximum classifier weight change: 0.00037988554686307907
- Class order: akiec, bcc, bkl, df, mel, nv, vasc

The classifier weights changed, confirming that the optimizer updated them. These results do not establish classification accuracy.

## Dependencies and remaining work

The loader and preprocessing come from the team's preprocessing task. They must be available alongside the classifier when running this script. Use the Data team's training manifest when available; keep validation and test images out of subsequent training steps.

## Reflection

I implemented and ran the training-step check and recorded its results. I learned how to verify that gradients and an optimizer update actually occur, rather than only checking model outputs. One remaining question is how the loss will behave across repeated batches once the training manifests are available.
