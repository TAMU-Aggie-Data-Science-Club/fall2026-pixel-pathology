# Week 3 — Streamlit app

## Setup and run

From the repository root, using a Python environment with pip:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app/app.py
```

Uploads work without HAM10000 data or a model checkpoint. For local sample
selection and known-label lookup, use:

```text
data/raw/HAM10000_metadata.csv
data/raw/HAM10000_images_part_1/
data/raw/HAM10000_images_part_2/
```

Keep original JPG filenames. Metadata configuration is documented in
[the Week 2 instructions](../week2/app.md#data).

## Current status and blocker

Known dataset labels are displayed separately from the model prediction section
and explicitly identified as metadata, not predictions. Uploaded images have no
known dataset label. Missing metadata produces a message and does not prevent
image viewing.

The Week 3 integration branch does not yet contain Modeling's prediction function
or a baseline checkpoint handoff. Predictions remain pending; the page displays
no predicted class or probability values. The class rows are placeholders, not
zero-probability predictions. Image viewing remains available during this handoff.
No checkpoint path or new prediction interface is introduced by this task.

The prediction integration task needs Modeling's loading/prediction functions,
checkpoint access, and agreed V2 prediction preprocessing. It must use
`CLASS_NAMES` and `CLASS_TO_IDX` from `src/model.py`, display the readable predicted
class and all seven probabilities, and preserve this pending behavior when a
checkpoint is missing. The current placeholder class-name dictionary remains for
the existing label display; it is not a model output contract.

The educational-use notice stays at the top of the page. Grad-CAM is explicitly
pending for Week 4; no heatmap is generated.

## Verification

Checks on October 25, 2026: all app files passed Python syntax parsing and
`git diff --check` passed. A dependency-free recording of Streamlit calls checked
the notice, seven pending rows, Week 4 message, known/upload/missing-metadata label
messages, and image-view calls while predictions were pending. These checks did
not render the page or run inference.

A live app check was blocked locally: installing the existing requirements under
MSYS2 Python failed while building pandas dependencies, ending in a CMake download
certificate-verification error. No requirements were changed. A member with the
documented app environment must still perform the launch checks below.

For another member or PM running the app:

1. Launch using the commands above with no model checkpoint. Confirm the
   educational-use notice, explicit prediction pending message, and Week 4
   Grad-CAM message appear.
2. Upload a valid JPG or PNG. Confirm the original image appears, the page says
   uploaded images have no known dataset label, and predictions stay pending.
3. With local HAM10000 data installed, select **HAM10000 sample**. Confirm the
   original image and its **Known dataset label** appear separately from
   **Model prediction**, with the metadata disclaimer.
4. Launch with metadata unavailable and select a sample. Confirm the metadata
   message appears and the original image still renders.
5. Upload an unreadable file with a JPG extension. Confirm a friendly error
   appears and the page remains usable.

Independent teammate launch and real baseline prediction evidence remain pending.
Do not count placeholder rows or this task's checks as a real model prediction.

## Contributions and next task

- **Abhlnaw — pending states and notices:** Clarified the baseline handoff blocker,
  kept metadata labels separate from model predictions, replaced zero-filled
  probability bars with pending text, retained the educational-use notice and
  image viewer, and marked Grad-CAM for Week 4. Added these run and check steps.

Next: connect Modeling's baseline handoff and have another member verify the
combined flow. Week 4 Grad-CAM depends on a working model/prediction handoff;
fine-tuning comparisons belong to Modeling's next task.
