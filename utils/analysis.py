from __future__ import annotations

import os
import re
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

import cv2
import nibabel as nib
import numpy as np


SUPPORTED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
SUPPORTED_VOLUME_SUFFIXES = {".nii", ".nii.gz"}


def _safe_normalize(array: np.ndarray) -> np.ndarray:
    array = array.astype(np.float32)
    min_value = float(np.min(array))
    max_value = float(np.max(array))
    if max_value - min_value < 1e-8:
        return np.zeros_like(array, dtype=np.float32)
    return (array - min_value) / (max_value - min_value)


def _sort_key(name: str) -> tuple:
    parts = re.split(r"(\d+)", name.lower())
    normalized = []
    for part in parts:
        normalized.append(int(part) if part.isdigit() else part)
    return tuple(normalized)


def _decode_image(raw: bytes) -> np.ndarray:
    image = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
    if image is None:
        raise ValueError("One of the uploaded image files could not be decoded.")
    return image


def _read_nifti_from_bytes(raw: bytes, filename: str) -> tuple[np.ndarray, tuple[float, float, float]]:
    suffix = ".nii.gz" if filename.lower().endswith(".nii.gz") else Path(filename).suffix
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(raw)
            temp_path = temp_file.name

        nifti = nib.load(temp_path)
        volume = nifti.get_fdata()
        spacing = tuple(float(x) for x in nifti.header.get_zooms()[:3])
        return volume, spacing
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def _volume_to_slices(volume: np.ndarray) -> list[np.ndarray]:
    volume = np.asarray(volume, dtype=np.float32)
    if volume.ndim == 4:
        volume = volume[..., 0]
    if volume.ndim != 3:
        raise ValueError("The uploaded MRI volume must be 3D.")

    volume = _safe_normalize(volume)
    return [volume[:, :, index] for index in range(volume.shape[2])]


def _extract_zip_entries(raw: bytes) -> list[tuple[str, bytes]]:
    entries: list[tuple[str, bytes]] = []
    with zipfile.ZipFile(BytesIO(raw)) as archive:
        for info in archive.infolist():
            if info.is_dir():
                continue
            entries.append((info.filename, archive.read(info.filename)))
    return entries


def load_study(uploaded_files: list) -> dict:
    if not uploaded_files:
        raise ValueError("Please upload at least one MRI image, archive, or volume.")

    files = sorted(uploaded_files, key=lambda item: _sort_key(item.name))
    first_name = files[0].name.lower()

    if len(files) == 1 and first_name.endswith(".zip"):
        entries = _extract_zip_entries(files[0].getvalue())
        image_entries = []
        volume_entry = None

        for filename, raw in sorted(entries, key=lambda item: _sort_key(item[0])):
            lower = filename.lower()
            if lower.endswith(".nii") or lower.endswith(".nii.gz"):
                volume_entry = (filename, raw)
                break
            if any(lower.endswith(ext) for ext in SUPPORTED_IMAGE_SUFFIXES):
                image_entries.append((filename, raw))

        if volume_entry:
            volume, spacing = _read_nifti_from_bytes(volume_entry[1], volume_entry[0])
            slices = _volume_to_slices(volume)
            return {
                "study_type": "nifti_zip",
                "source_name": volume_entry[0],
                "slices": slices,
                "spacing": spacing,
            }

        if not image_entries:
            raise ValueError("The ZIP file does not contain supported MRI images.")

        slices = [_safe_normalize(_decode_image(raw)) for _, raw in image_entries]
        return {
            "study_type": "image_zip",
            "source_name": files[0].name,
            "slices": slices,
            "spacing": None,
        }

    if len(files) == 1 and (first_name.endswith(".nii") or first_name.endswith(".nii.gz")):
        volume, spacing = _read_nifti_from_bytes(files[0].getvalue(), files[0].name)
        return {
            "study_type": "nifti",
            "source_name": files[0].name,
            "slices": _volume_to_slices(volume),
            "spacing": spacing,
        }

    slices = []
    for uploaded_file in files:
        if not any(uploaded_file.name.lower().endswith(ext) for ext in SUPPORTED_IMAGE_SUFFIXES):
            raise ValueError("For folder-style uploads, use PNG/JPG/JPEG slices or a ZIP archive.")
        slices.append(_safe_normalize(_decode_image(uploaded_file.getvalue())))

    return {
        "study_type": "image_stack" if len(slices) > 1 else "single_image",
        "source_name": files[0].name if len(files) == 1 else f"{len(files)} MRI slices",
        "slices": slices,
        "spacing": None,
    }


def run_segmentation(study: dict, model, target_size: tuple[int, int] = (128, 128), threshold: float = 0.5) -> dict:
    slices = study["slices"]
    if not slices:
        raise ValueError("No MRI slices were loaded for analysis.")

    base_height, base_width = slices[0].shape[:2]
    aligned_slices = []
    network_inputs = []

    for current_slice in slices:
        aligned_slice = current_slice
        if current_slice.shape[:2] != (base_height, base_width):
            aligned_slice = cv2.resize(current_slice, (base_width, base_height), interpolation=cv2.INTER_LINEAR)
        aligned_slices.append(aligned_slice)

        resized = cv2.resize(aligned_slice, target_size, interpolation=cv2.INTER_AREA)
        network_inputs.append(resized)

    batch = np.stack(network_inputs, axis=0).astype(np.float32)
    batch = batch.reshape(batch.shape[0], target_size[1], target_size[0], 1)

    if model is None:
        probabilities = np.zeros((len(aligned_slices), base_height, base_width), dtype=np.float32)
    else:
        predictions = model.predict(batch, verbose=0)
        probabilities = []
        for prediction in predictions:
            probability_map = prediction[:, :, 0]
            resized = cv2.resize(probability_map, (base_width, base_height), interpolation=cv2.INTER_LINEAR)
            probabilities.append(resized)
        probabilities = np.stack(probabilities, axis=0).astype(np.float32)

    masks = (probabilities >= threshold).astype(np.uint8)
    volume = np.stack(aligned_slices, axis=0)

    return {
        "volume": volume,
        "probabilities": probabilities,
        "masks": masks,
        "spacing": study.get("spacing"),
        "study_type": study["study_type"],
        "source_name": study["source_name"],
    }


def _estimate_region(mask_volume: np.ndarray) -> str:
    points = np.argwhere(mask_volume > 0)
    if len(points) == 0:
        return "No abnormal region detected"

    z_mean, y_mean, x_mean = points.mean(axis=0)
    depth, height, width = mask_volume.shape

    hemisphere = "Left" if x_mean < width / 2 else "Right"

    y_ratio = y_mean / max(height, 1)
    z_ratio = z_mean / max(depth, 1)

    if y_ratio < 0.28:
        lobe = "Frontal"
    elif y_ratio < 0.5:
        lobe = "Parietal"
    elif y_ratio < 0.72:
        lobe = "Temporal"
    else:
        lobe = "Occipital"

    if z_ratio > 0.78:
        lobe = "Cerebellar / posterior fossa"

    return f"{hemisphere} {lobe}"


def _burden_level(affected_percent: float) -> str:
    if affected_percent < 0.3:
        return "No significant burden"
    if affected_percent < 2:
        return "Low"
    if affected_percent < 8:
        return "Moderate"
    if affected_percent < 20:
        return "High"
    return "Critical"


def _pattern_label(mask_volume: np.ndarray, affected_percent: float) -> str:
    positive_slices = int(np.count_nonzero(mask_volume.reshape(mask_volume.shape[0], -1).sum(axis=1)))
    if affected_percent < 0.3:
        return "No tumor pattern detected"
    if positive_slices <= 2 and affected_percent < 2:
        return "Localized focal lesion pattern"
    if affected_percent < 8:
        return "Intermediate focal tumor pattern"
    return "Diffuse large-volume tumor pattern"


def summarize_analysis(segmentation: dict) -> dict:
    volume = segmentation["volume"]
    masks = segmentation["masks"]
    probabilities = segmentation["probabilities"]

    brain_mask = volume > max(float(np.percentile(volume, 35)), 0.08)
    tumor_voxels = int(np.count_nonzero(masks))
    brain_voxels = max(int(np.count_nonzero(brain_mask)), 1)
    affected_percent = (tumor_voxels / brain_voxels) * 100.0

    spacing = segmentation.get("spacing")
    voxel_volume_mm3 = None
    affected_volume_mm3 = None
    if spacing and len(spacing) == 3:
        voxel_volume_mm3 = float(spacing[0] * spacing[1] * spacing[2])
        affected_volume_mm3 = tumor_voxels * voxel_volume_mm3

    confidence = float(np.max(probabilities)) * 100.0 if tumor_voxels else float(100.0 - np.mean(probabilities) * 100.0)
    probability_inside_mask = float(np.mean(probabilities[masks > 0])) * 100.0 if tumor_voxels else 0.0

    slice_burden = masks.reshape(masks.shape[0], -1).sum(axis=1)
    peak_slice_index = int(np.argmax(slice_burden)) if tumor_voxels else 0

    return {
        "detected": tumor_voxels > 0,
        "affected_percent": affected_percent,
        "tumor_voxels": tumor_voxels,
        "brain_voxels": brain_voxels,
        "voxel_volume_mm3": voxel_volume_mm3,
        "affected_volume_mm3": affected_volume_mm3,
        "estimated_region": _estimate_region(masks),
        "tumor_level": _burden_level(affected_percent),
        "tumor_pattern": _pattern_label(masks, affected_percent),
        "tumor_type": "Classification unavailable in current model",
        "confidence_percent": confidence,
        "inside_mask_probability_percent": probability_inside_mask,
        "positive_slice_count": int(np.count_nonzero(slice_burden)),
        "total_slice_count": int(masks.shape[0]),
        "peak_slice_index": peak_slice_index,
    }
