"""Grad-CAM checks on an untrained model; these do not evaluate model quality."""

from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image
import streamlit as st
from streamlit.testing.v1 import AppTest
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))
sys.path.insert(0, str(ROOT / "src"))

from gradcam import grad_cam_map, overlay_heatmap
from model import NUM_CLASSES, build_model


def make_model():
    torch.manual_seed(0)
    model = build_model(pretrained=False)
    model.eval()
    return model


class GradCamTests(unittest.TestCase):
    def setUp(self):
        self.model = make_model()
        self.batch = torch.randn(1, 3, 224, 224)

    def test_matches_classic_cam(self):
        # ResNet-50 ends in average pooling then one linear layer, so Grad-CAM
        # must equal the classic CAM built from that layer's weights.
        top, heatmap = grad_cam_map(self.model, self.batch)

        captured = []
        hook = self.model.layer4[-1].register_forward_hook(lambda m, i, o: captured.append(o))
        with torch.no_grad():
            logits = self.model(self.batch)
        hook.remove()
        self.assertEqual(top, int(logits.argmax()))
        cam = F.relu(torch.einsum("c,chw->hw", self.model.fc.weight[top], captured[0][0]))
        cam = F.interpolate(cam[None, None], size=(224, 224), mode="bilinear", align_corners=False)[0, 0]
        cam = cam / cam.max()
        self.assertTrue(torch.allclose(heatmap, cam, atol=1e-4))

    def test_heatmap_shape_and_range(self):
        _, heatmap = grad_cam_map(self.model, self.batch)
        self.assertEqual(tuple(heatmap.shape), (224, 224))
        self.assertTrue(torch.isfinite(heatmap).all())
        self.assertGreaterEqual(heatmap.min().item(), 0)
        self.assertLessEqual(heatmap.max().item(), 1)

    def test_works_with_frozen_backbone_and_leaves_no_hooks(self):
        for name, parameter in self.model.named_parameters():
            parameter.requires_grad = name.startswith("fc.")
        top, _ = grad_cam_map(self.model, self.batch)
        self.assertIn(top, range(NUM_CLASSES))
        self.assertEqual(len(self.model.layer4[-1]._forward_hooks), 0)

    def test_overlay_is_a_valid_image(self):
        original = np.random.rand(224, 224, 3)
        overlay = overlay_heatmap(original, np.random.rand(224, 224))
        self.assertEqual(overlay.shape, (224, 224, 3))
        self.assertGreaterEqual(overlay.min(), 0)
        self.assertLessEqual(overlay.max(), 1)

    def test_does_not_change_callers_tensor(self):
        grad_cam_map(self.model, self.batch)
        self.assertFalse(self.batch.requires_grad)


class GradCamPageTests(unittest.TestCase):
    def setUp(self):
        st.cache_resource.clear()
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        folder = Path(temp.name)
        image = folder / "sample.jpg"
        Image.fromarray((np.random.rand(64, 64, 3) * 255).astype("uint8")).save(image)
        checkpoint = folder / "baseline.pt"
        checkpoint.write_bytes(b"placeholder")
        self.patch("model.CHECKPOINT_PATH", str(checkpoint))
        self.load = self.patch("predict.load_model", return_value=make_model())
        self.patch("predict.predict_probabilities", return_value=[1 / 7] * 7)
        self.patch("sample_input.find_samples", return_value={"sample": str(image)})
        self.patch("known_label.load_labels", return_value={"sample": "mel"})

    def patch(self, target, *args, **kwargs):
        patcher = patch(target, *args, **kwargs)
        value = patcher.start()
        self.addCleanup(patcher.stop)
        return value

    @staticmethod
    def image_captions(app):
        return [img.caption for element in app.get("image") for img in element.proto.imgs]

    def page(self):
        app = AppTest.from_file(str(ROOT / "app" / "app.py"), default_timeout=60).run()
        app.radio[0].set_value("HAM10000 sample").run()
        self.assertEqual(len(app.exception), 0)
        return app

    def test_shows_original_and_overlay_for_predicted_class(self):
        app = self.page()
        text = "\n".join(item.value for item in app.markdown)
        self.assertIn("Step 3 – Grad-CAM heatmap", text)
        self.assertIn("Heatmap for the predicted class:", text)
        captions = self.image_captions(app)
        self.assertIn("Grad-CAM overlay", captions)
        self.assertTrue(any("do not mark exact lesion boundaries" in c.value for c in app.caption))

    def test_failure_falls_back_to_pending_without_overlay(self):
        self.load.side_effect = ValueError("class order mismatch")
        app = self.page()
        text = "\n".join(item.value for item in app.markdown)
        self.assertNotIn("Grad-CAM heatmap", text)
        self.assertTrue(any("Pending" in c.value for c in app.caption))
        captions = self.image_captions(app)
        self.assertNotIn("Grad-CAM overlay", captions)


if __name__ == "__main__":
    unittest.main()
