# App: final model (Week 7)

The app now uses the final fine-tuned model, `finetune_layer34.pt` (layer3 + layer4 + head fine-tuned with weighted sampling). Details and test-set results are in [final_model.md](final_model.md).

## Checkpoint

On startup, if `models/finetune_layer34.pt` is missing, the app downloads it from the
[model-finetune-layer34-v1 release](https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-pixel-pathology/releases/tag/model-finetune-layer34-v1)
and checks its SHA-256 (`a22ca8119ecb8c69c274ba12589ed7b2213ae720c5fdde7ade5cdd0c34f9fabd`).
A file that fails the check is discarded. The URL, filename and hash live in `app/checkpoint.py`; update them there if the release file is replaced.

If the download fails, the page shows "the final checkpoint is missing". You can download the file from the release yourself and put it in `models/`.

## Confusion matrix

The page shows `docs/week7/figures/confusion_matrix_test.png`: the saved evaluation of the final model on the 1,494-image test split. It is separate from the prediction for the selected image.
