"""Download the final checkpoint on first run (needed for Streamlit Cloud).

models/ is git-ignored, so a fresh deploy has no checkpoint. If the file is
missing we fetch it from the GitHub Release and verify its SHA-256.
If the release file is ever replaced, update the three constants below.
"""
import hashlib
import shutil
import ssl
import urllib.request
from pathlib import Path

CHECKPOINT_FILENAME = "finetune_layer34.pt"
CHECKPOINT_URL = (
    "https://github.com/TAMU-Aggie-Data-Science-Club/fall2026-pixel-pathology/"
    "releases/download/model-finetune-layer34-v1/finetune_layer34.pt"
)
CHECKPOINT_SHA256 = "a22ca8119ecb8c69c274ba12589ed7b2213ae720c5fdde7ade5cdd0c34f9fabd"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def ensure_checkpoint(path: Path) -> Path:
    """Return path, downloading and verifying the checkpoint if it is missing."""
    path = Path(path)
    if path.exists():
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".part")
    try:
        try:
            import certifi

            context = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            context = ssl.create_default_context()
        with urllib.request.urlopen(CHECKPOINT_URL, context=context) as response, tmp.open("wb") as out:
            shutil.copyfileobj(response, out)
        actual = _sha256(tmp)
        if actual != CHECKPOINT_SHA256:
            raise RuntimeError(
                f"Downloaded {CHECKPOINT_FILENAME} has SHA-256 {actual}, "
                f"expected {CHECKPOINT_SHA256}."
            )
        tmp.replace(path)
    finally:
        tmp.unlink(missing_ok=True)
    return path
