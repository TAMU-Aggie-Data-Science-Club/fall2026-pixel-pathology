"""The team's saved validation matrix, labeled separately from live inference."""
from pathlib import Path

import streamlit as st

from checkpoint_identity import checkpoint_identity

# Published in docs/week6/app.md at integration commit c225547.
WEIGHTED_SHA256 = "a77cee14c7c19292fe93ad2164888ebaff7723ac59da5511c341d6fe35d82bc9"
MATRIX_PATH = Path(__file__).resolve().parent.parent / "docs" / "week4" / "weighted_sampling_matrix.png"


def verification_message(identity):
    if identity is None:
        return "Not verified against the app's checkpoint: no checkpoint file is available."
    if identity["sha256"] == WEIGHTED_SHA256:
        return "Matches the app's selected checkpoint file (SHA-256 verified)."
    return (
        "Not verified against the app's checkpoint. These results describe the documented "
        f"weighted_sampling.pt; the local file {identity['name']} has a different SHA-256."
    )


def show_confusion_matrix():
    st.subheader("Model performance — Confusion matrix")
    st.markdown("**Model:** ResNet-50 with weighted sampling — `weighted_sampling.pt`")
    st.markdown("**Split:** Validation — 1,519 HAM10000 images")
    st.caption(verification_message(checkpoint_identity()))
    if MATRIX_PATH.is_file():
        st.image(
            str(MATRIX_PATH),
            caption="ResNet-50 with weighted sampling (weighted_sampling.pt) — validation split, 1,519 images",
        )
    else:
        st.info("The saved confusion matrix is missing. Restore docs/week4/weighted_sampling_matrix.png from the team's integration branch.")
    st.caption(
        "Rows are true dataset labels; columns are model predictions. Values are image counts. "
        "This is the saved validation evaluation of weighted_sampling.pt, separate from "
        "the selected image's prediction. It does not report test-set or clinical performance."
    )
