"""File identity for the checkpoint shown in the interface.

This only reads the file's bytes and metadata. It never loads it as a model and never
claims it matches any documented checkpoint or attaches any metrics to it.
"""

from datetime import datetime
import hashlib
from pathlib import Path

import streamlit as st

import prediction  # noqa: F401  (puts src/ on sys.path)


@st.cache_data(show_spinner=False)
def _sha256(path, modified_ns, size):
    """Hash once per file version. Arguments only key the cache."""
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def checkpoint_identity():
    """Return {name, sha256, short, size, modified} for the checkpoint file, or None."""
    try:
        path = Path(prediction.DEMO_CHECKPOINT_PATH)
        info = path.stat()
        digest = _sha256(str(path), info.st_mtime_ns, info.st_size)
    except Exception:
        return None
    return {
        "name": path.name,
        "sha256": digest,
        "short": digest[:12],
        "size": f"{info.st_size / 1e6:.1f} MB",
        "modified": datetime.fromtimestamp(info.st_mtime).strftime("%b %d, %Y"),
    }
