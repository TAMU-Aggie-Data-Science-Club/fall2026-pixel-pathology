"""Connect the page to Modeling's shared prediction interface."""

import math
from pathlib import Path
import sys

import streamlit as st

# Modeling's modules import each other by bare name (see its handoff docs).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


@st.cache_resource
def load_cached_model(checkpoint_path, modified_ns, size):
    """Reuse the model until the checkpoint is replaced or the app restarts."""
    from predict import load_model

    return load_model(checkpoint_path, device="cpu")


def show_prediction(source, readable_names):
    """Display real probabilities, or a pending message without stopping the page."""
    st.divider()
    st.markdown("#### Step 2 – Model prediction")
    st.caption("Known dataset labels above come from metadata, not from the model.")
    if source is None:
        st.info("Prediction pending — upload or select an image to begin.")
        return

    try:
        from model import CHECKPOINT_PATH, CLASS_NAMES
        from predict import predict_probabilities

        checkpoint = Path(CHECKPOINT_PATH)
        identity = checkpoint.stat()
        model = load_cached_model(str(checkpoint), identity.st_mtime_ns, identity.st_size)
    except FileNotFoundError:
        st.info(
            "Prediction pending — the baseline checkpoint is missing. "
            "Follow docs/week3/checkpoint_and_prediction.md to obtain it. "
            "You can still view your image."
        )
        return
    except ImportError:
        st.info(
            "Prediction pending — install Modeling's dependencies using the "
            "setup instructions in docs/week4/app.md. You can still view your image."
        )
        return
    except Exception:
        st.warning(
            "Prediction unavailable — the checkpoint could not be loaded. "
            "Check that it is Modeling's agreed seven-class checkpoint. "
            "You can still view your image."
        )
        return

    try:
        probabilities = predict_probabilities(model, source)
        if (
            len(probabilities) != len(CLASS_NAMES)
            or not all(math.isfinite(p) and 0 <= p <= 1 for p in probabilities)
            or not math.isclose(sum(probabilities), 1, abs_tol=1e-4)
        ):
            raise ValueError("Expected seven probabilities summing to one.")
    except Exception:
        st.warning(
            "Prediction unavailable — the image could not be processed. "
            "Choose a valid JPG or PNG; no model result is shown."
        )
        return

    top = max(range(len(CLASS_NAMES)), key=probabilities.__getitem__)
    code = CLASS_NAMES[top]
    st.markdown(f"##### Predicted class: {readable_names[code]} ({code})")
    st.write(f"Model probability: {probabilities[top]:.2%}")
    st.table([
        {"Code": code, "Class": readable_names[code], "Model probability": f"{probability:.2%}"}
        for code, probability in zip(CLASS_NAMES, probabilities)
    ])
    st.caption(
        "These are model probabilities, not a diagnosis or proof of correctness. "
        "Educational and research use only."
    )
