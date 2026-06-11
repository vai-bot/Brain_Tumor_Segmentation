from __future__ import annotations

import os
from pathlib import Path

import cv2
import numpy as np

try:
    from tensorflow.keras.models import load_model
except Exception:  # pragma: no cover - tensorflow is already a runtime dependency
    load_model = None


ROOT_DIR = Path(__file__).resolve().parents[1]
CLASSIFIER_PATH = ROOT_DIR / "model" / "tumor_classifier.h5"
DEFAULT_LABELS = ("Glioma", "Meningioma", "Pituitary")


def get_classifier_model():
    if load_model is None or not CLASSIFIER_PATH.exists():
        return None
    try:
        return load_model(CLASSIFIER_PATH)
    except Exception:
        return None


def _classifier_labels(output_units: int) -> list[str]:
    configured = os.getenv("TUMOR_CLASS_LABELS")
    if configured:
        labels = [label.strip() for label in configured.split(",") if label.strip()]
        if len(labels) == output_units:
            return labels
    if output_units == len(DEFAULT_LABELS):
        return list(DEFAULT_LABELS)
    return [f"Class {index + 1}" for index in range(output_units)]


def _prepare_classifier_input(segmentation: dict) -> np.ndarray:
    slice_burden = segmentation["masks"].reshape(segmentation["masks"].shape[0], -1).sum(axis=1)
    peak_slice_index = int(np.argmax(slice_burden)) if int(np.max(slice_burden)) > 0 else segmentation["volume"].shape[0] // 2
    peak_slice = segmentation["volume"][peak_slice_index]
    resized = cv2.resize(peak_slice, (224, 224), interpolation=cv2.INTER_AREA).astype(np.float32)
    three_channel = np.repeat(resized[:, :, np.newaxis], 3, axis=2)
    return np.expand_dims(three_channel, axis=0)


def _heuristic_type(segmentation: dict, summary: dict) -> dict:
    if not summary["detected"]:
        return {
            "tumor_type": "No tumor detected",
            "tumor_type_source": "Segmentation result",
            "tumor_type_confidence": 100.0,
        }

    region = summary["estimated_region"].lower()
    affected = float(summary["affected_percent"])
    slice_ratio = summary["positive_slice_count"] / max(summary["total_slice_count"], 1)

    if "cerebellar" in region:
        label = "Posterior fossa lesion pattern"
    elif affected > 8 or slice_ratio > 0.3:
        label = "Glioma-like infiltrative pattern"
    elif "frontal" in region or "parietal" in region:
        label = "Meningioma-like focal pattern"
    else:
        label = "Pituitary or focal sellar-adjacent pattern"

    confidence = min(82.0, max(42.0, summary["confidence_percent"] * 0.72))
    return {
        "tumor_type": label,
        "tumor_type_source": "Heuristic estimate",
        "tumor_type_confidence": round(confidence, 1),
    }


def classify_tumor_type(segmentation: dict, summary: dict, classifier_model=None) -> dict:
    if classifier_model is not None:
        try:
            batch = _prepare_classifier_input(segmentation)
            predictions = classifier_model.predict(batch, verbose=0)[0]
            probabilities = np.asarray(predictions, dtype=np.float32)
            if probabilities.ndim == 0:
                raise ValueError("Classifier output shape is invalid.")
            class_index = int(np.argmax(probabilities))
            labels = _classifier_labels(int(probabilities.shape[0]))
            return {
                "tumor_type": labels[class_index],
                "tumor_type_source": "Classifier model",
                "tumor_type_confidence": round(float(probabilities[class_index]) * 100.0, 1),
            }
        except Exception:
            pass

    return _heuristic_type(segmentation, summary)
