"""Checkpoint identity and real-output replay regression checks."""
import base64
import hashlib
import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "src"))

from checkpoint_identity import checkpoint_identity
from demo_outputs import Outputs, OK, NO_IMAGE, get_outputs
from flow_payload import build_payload
from gradcam import overlay_heatmap
from model import CLASS_NAMES
from results_panel import WEIGHTED_SHA256, verification_message


class PresentationHelperTests(unittest.TestCase):
    def setUp(self):
        st.cache_data.clear()
        st.cache_resource.clear()

    def test_results_require_full_hash_match(self):
        self.assertIn("Matches the app\'s selected checkpoint file", verification_message(
            {"name": "weighted_sampling.pt", "sha256": WEIGHTED_SHA256}))
        for digest in (WEIGHTED_SHA256[:12], "0" * 64):
            self.assertIn("Not verified", verification_message(
                {"name": "weighted_sampling.pt", "sha256": digest}))
        self.assertIn("Not verified", verification_message(None))

    def test_identity_uses_team_path_and_updates_after_replacement(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "weighted_sampling.pt"
            with patch("prediction.DEMO_CHECKPOINT_PATH", path):
                self.assertIsNone(checkpoint_identity())
                path.write_bytes(b"first")
                self.assertEqual(checkpoint_identity()["sha256"], hashlib.sha256(b"first").hexdigest())
                path.write_bytes(b"replacement with new size")
                self.assertEqual(checkpoint_identity()["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())

    def make_outputs(self):
        crop = np.full((224, 224, 3), 0.4)
        heatmap = np.tile(np.linspace(0, 1, 224), (224, 1))
        return Outputs(status=OK, original=Image.new("RGB", (300, 250), "white"),
                       original_size=(300, 250), class_codes=CLASS_NAMES,
                       probabilities=[.02, .03, .04, .01, .08, .80, .02], top=5,
                       crop=crop, heatmap=heatmap, heatmap_class=5,
                       overlay=overlay_heatmap(crop, heatmap))

    def test_replay_uses_existing_outputs_without_inference(self):
        outputs = self.make_outputs()
        with patch("predict.predict_probabilities", side_effect=AssertionError("No replay inference")):
            payload, signature = build_payload(outputs, None)
        self.assertEqual([row["p"] for row in payload["classes"]], outputs.probabilities)
        self.assertEqual(payload["top"], 5)
        self.assertTrue(payload["heatmapReady"])
        self.assertIn("CONCEPTUAL ILLUSTRATION", payload["copy"]["C"]["tag"])
        self.assertTrue(signature)

    def test_replay_overlay_matches_demo_with_image_quantization_tolerance(self):
        outputs = self.make_outputs()
        payload, _ = build_payload(outputs, None)
        def decode(key):
            data = base64.b64decode(payload["images"][key].split(",", 1)[1])
            return np.asarray(Image.open(io.BytesIO(data))).astype(float) / 255
        replay = .5 * decode("crop") + .5 * decode("colorLayer")
        self.assertTrue(np.allclose(replay, outputs.overlay, atol=1/255))

    def test_new_image_or_checkpoint_resets_replay_signature(self):
        outputs = self.make_outputs()
        _, initial = build_payload(outputs, None)
        outputs.original = Image.new("RGB", (300, 250), "black")
        _, changed_image = build_payload(outputs, None)
        self.assertNotEqual(initial, changed_image)
        _, changed_checkpoint = build_payload(outputs, {
            "name": "weighted_sampling.pt", "sha256": WEIGHTED_SHA256, "short": WEIGHTED_SHA256[:12]})
        self.assertNotEqual(changed_image, changed_checkpoint)

    def test_empty_page_has_no_invented_prediction(self):
        payload, _ = build_payload(Outputs(status=NO_IMAGE), None)
        self.assertFalse(payload["ready"])
        self.assertEqual(payload["classes"], [])
        self.assertIsNone(payload["top"])
        self.assertFalse(payload["heatmapReady"])

    def test_real_inference_matches_shared_predictor(self):
        # Random model weights exercise the real code path, not model quality.
        from model import build_model
        from predict import predict_probabilities
        model = build_model(pretrained=False).eval()
        with tempfile.TemporaryDirectory() as folder:
            checkpoint = Path(folder) / "weighted_sampling.pt"
            checkpoint.write_bytes(b"path identity only; loader mocked below")
            image = Path(folder) / "sample.png"
            Image.new("RGB", (300, 250), "pink").save(image)
            expected = predict_probabilities(model, image)
            with patch("prediction.DEMO_CHECKPOINT_PATH", checkpoint), \
                 patch("predict.load_model", return_value=model):
                outputs = get_outputs(image)
            self.assertEqual(outputs.status, OK)
            self.assertTrue(np.allclose(outputs.probabilities, expected, atol=1e-7))
            self.assertEqual(outputs.top, outputs.heatmap_class)
            self.assertEqual(outputs.crop.shape, (224, 224, 3))
            self.assertEqual(outputs.heatmap.shape, (224, 224))
            self.assertTrue(np.isfinite(outputs.overlay).all())

    def test_rerun_reuses_inference_until_checkpoint_changes(self):
        with tempfile.TemporaryDirectory() as folder:
            checkpoint = Path(folder) / "weighted_sampling.pt"
            checkpoint.write_bytes(b"checkpoint")
            image = Path(folder) / "sample.png"
            Image.new("RGB", (32, 32), "white").save(image)
            with patch("prediction.DEMO_CHECKPOINT_PATH", checkpoint), \
                 patch("predict.load_model", return_value=object()), \
                 patch("predict.predict_probabilities", return_value=[1/7]*7) as predict:
                get_outputs(image)
                get_outputs(image)
                self.assertEqual(predict.call_count, 1)
                checkpoint.write_bytes(b"replacement checkpoint with different size")
                get_outputs(image)
                self.assertEqual(predict.call_count, 2)


if __name__ == "__main__":
    unittest.main()
