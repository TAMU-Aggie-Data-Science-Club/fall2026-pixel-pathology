"""Page regressions with controlled inference; these do not evaluate model quality."""

import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image
import streamlit as st
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "src"))

from model import CLASS_NAMES
from notices import CLASS_NAMES as READABLE_NAMES


class PredictionPageTests(unittest.TestCase):
    def setUp(self):
        st.cache_resource.clear()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.image = self.folder / "sample.jpg"
        Image.new("RGB", (32, 32), "white").save(self.image)
        self.checkpoint = self.folder / "baseline.pt"
        self.checkpoint.write_bytes(b"test checkpoint placeholder")
        self.patch("model.CHECKPOINT_PATH", str(self.checkpoint))
        self.load = self.patch("predict.load_model", return_value=object())
        self.predict = self.patch(
            "predict.predict_probabilities", return_value=[0.02, 0.03, 0.04, 0.01, 0.08, 0.80, 0.02]
        )
        self.patch("sample_input.find_samples", return_value={"sample": str(self.image)})
        self.labels = self.patch("known_label.load_labels", return_value={"sample": "mel"})

    def patch(self, target, *args, **kwargs):
        patcher = patch(target, *args, **kwargs)
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    def page(self, sample=True):
        app = AppTest.from_file(str(ROOT / "app" / "app.py"), default_timeout=30).run()
        if sample:
            app.radio[0].set_value("HAM10000 sample").run()
        self.assertEqual(len(app.exception), 0)
        self.assertTrue(any("EDUCATIONAL" in item.value for item in app.markdown))
        return app

    def assert_viewer(self, app):
        self.assertTrue(
            app.get("image") or app.get("imgs"), "Original image should remain visible"
        )

    def test_no_image_does_not_infer(self):
        app = self.page(sample=False)
        self.predict.assert_not_called()
        self.assertTrue(any("upload or select" in item.value for item in app.info))
        self.assertEqual(len(app.table), 0)

    def test_known_label_and_prediction_are_distinct_and_ordered(self):
        app = self.page()
        text = "\n".join(item.value for item in app.markdown)
        self.assertIn("Known dataset label", text)
        self.assertIn("mel — Melanoma", text)
        self.assertIn("Predicted class: Melanocytic nevi (nv)", text)
        table = app.table[0].value
        self.assertEqual(list(table["Code"]), CLASS_NAMES)
        self.assertEqual(list(table["Class"]), [READABLE_NAMES[c] for c in CLASS_NAMES])
        self.assertEqual(list(table["Model probability"])[5], "80.00%")
        self.assertIn("Model probability: 80.00%", text)
        self.assert_viewer(app)
        app.run()
        self.assertEqual(self.load.call_count, 1)
        self.checkpoint.write_bytes(b"replacement checkpoint with a different size")
        app.run()
        self.assertEqual(self.load.call_count, 2)

    def test_missing_checkpoint_keeps_viewer_and_no_results(self):
        self.checkpoint.unlink()
        app = self.page()
        self.assertTrue(any("checkpoint is missing" in item.value for item in app.info))
        self.predict.assert_not_called()
        self.assertEqual(len(app.table), 0)
        self.assert_viewer(app)

    def test_incompatible_checkpoint_keeps_viewer(self):
        self.load.side_effect = ValueError("class order mismatch")
        app = self.page()
        self.assertTrue(any("checkpoint could not be loaded" in item.value for item in app.warning))
        self.predict.assert_not_called()
        self.assertEqual(len(app.table), 0)
        self.assert_viewer(app)

    def test_missing_metadata_does_not_block_inference(self):
        self.labels.return_value = None
        app = self.page()
        self.assertTrue(any("metadata not found" in item.value for item in app.info))
        self.assertEqual(len(app.table), 1)
        self.assert_viewer(app)

    def test_upload_is_rewound_for_viewing_after_inference(self):
        upload = io.BytesIO(self.image.read_bytes())
        self.patch("sample_input.choose_image", return_value=(upload, None))

        def consume_upload(model, source):
            source.read()
            return [0.02, 0.03, 0.04, 0.01, 0.08, 0.80, 0.02]

        self.predict.side_effect = consume_upload
        app = self.page(sample=False)
        self.assertTrue(any("Uploaded images" in item.value for item in app.caption))
        self.assertEqual(len(app.table), 1)
        self.assert_viewer(app)

    def test_unreadable_image_leaves_page_usable(self):
        self.image.write_bytes(b"not an image")
        self.predict.side_effect = OSError("cannot identify image")
        app = self.page()
        self.assertTrue(any("image could not be processed" in item.value for item in app.warning))
        self.assertTrue(any("Couldn't read" in item.value for item in app.error))
        self.assertEqual(len(app.table), 0)

    def test_invalid_probabilities_are_not_displayed(self):
        for probabilities in ([0.5], [float("nan")] * 7, [0.5] * 7):
            with self.subTest(probabilities=probabilities):
                self.predict.return_value = probabilities
                app = self.page()
                self.assertEqual(len(app.table), 0)
                self.assertTrue(app.warning)
                self.assert_viewer(app)


if __name__ == "__main__":
    unittest.main()
