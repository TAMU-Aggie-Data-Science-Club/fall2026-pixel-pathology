"""The team's saved test matrix, labeled separately from live inference."""
import json
from pathlib import Path

import streamlit as st

from checkpoint_identity import checkpoint_identity

# Release model-finetune-layer34-v1; results from main commit 6435415.
FINAL_MODEL_SHA256 = "a22ca8119ecb8c69c274ba12589ed7b2213ae720c5fdde7ade5cdd0c34f9fabd"
MATRIX_PATH = Path(__file__).resolve().parent.parent / "docs" / "week7" / "figures" / "confusion_matrix_test.png"

METRICS_PATH = Path(__file__).resolve().parent.parent / "docs" / "week7" / "results" / "finetune_layer34_test_metrics.json"


def verification_message(identity):
    if identity is None:
        return "Not verified against the app's checkpoint: no checkpoint file is available."
    if identity["sha256"] == FINAL_MODEL_SHA256:
        return "Matches the app's selected checkpoint file (SHA-256 verified)."
    return (
        "Not verified against the app's checkpoint. These results describe the documented "
        f"finetune_layer34.pt; the local file {identity['name']} has a different SHA-256."
    )


def show_confusion_matrix():
    st.subheader("Model performance — Confusion matrix")
    st.markdown("**Model:** ResNet-50 fine-tuned layers 3 + 4 — `finetune_layer34.pt`")
    st.markdown("**Split:** Test — 1,494 HAM10000 images")
    st.caption(verification_message(checkpoint_identity()))
    # Published test metrics, kept separate from the selected image's probability.
    if METRICS_PATH.is_file():
        metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
        matrix = metrics["confusion_matrix"]
        total = sum(sum(row) for row in matrix)
        accuracy = sum(matrix[i][i] for i in range(len(matrix))) / total
        columns = st.columns(4)
        columns[0].metric("7-class macro F1", f"{metrics['macro_f1']:.3f}")
        columns[1].metric("Test accuracy", f"{accuracy:.1%}")
        columns[2].metric("Binary macro F1", f"{metrics['benign_vs_malignant']['binary_macro_f1']:.3f}")
        columns[3].metric("Grouped sensitivity", f"{metrics['benign_vs_malignant']['sensitivity']:.1%}")
        st.caption(
            "Binary metrics group akiec, bcc and mel as malignant or pre-cancerous, "
            "and the other four categories as benign. These are saved test-set results, "
            "not the selected image's probability."
        )
    if MATRIX_PATH.is_file():
        st.image(
            str(MATRIX_PATH),
            caption="ResNet-50 fine-tuned layers 3 + 4 (finetune_layer34.pt) — test split, 1,494 images",
        )
    else:
        st.info("The saved confusion matrix is missing. Restore docs/week7/figures/confusion_matrix_test.png from main's Week 7 figures.")
    st.caption(
        "Rows are true dataset labels; columns are model predictions. Cells show image counts and percentages within each true-label row. "
        "This is the saved test evaluation of finetune_layer34.pt, separate from "
        "the selected image's prediction. It reports held-out dataset performance, not clinical performance."
    )
    st.caption(
        "The final model's probabilities are not calibrated: it can be highly confident and wrong. "
        "Melanoma recall on this test set was 65.8%; rare-class results are based on small samples. "
        "See docs/week7/final_model.md for the full results and limitations."
    )
