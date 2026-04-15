import nibabel as nib
import numpy as np
import cv2
import os

def load_mri(path):
    return nib.load(path).get_fdata()

def normalize(image):
    return (image - np.min(image)) / (np.max(image) - np.min(image))


def save_slices(image, mask, output_dir="data/processed"):
    image = normalize(image)

    img_dir = os.path.join(output_dir, "images")
    mask_dir = os.path.join(output_dir, "masks")

    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(mask_dir, exist_ok=True)

    count = 0

    for i in range(image.shape[2]):  # iterate over slices

        img_slice = image[:, :, i]
        mask_slice = mask[:, :, i]

        # Skip slices without tumor
        if np.max(mask_slice) == 0:
            continue

        # Resize to fixed size
        img_slice = cv2.resize(img_slice, (128, 128))
        mask_slice = cv2.resize(mask_slice, (128, 128))

        # Convert to uint8
        img_slice = (img_slice * 255).astype(np.uint8)
        mask_slice = (mask_slice * 255).astype(np.uint8)

        # Save images
        cv2.imwrite(f"{img_dir}/img_{count}.png", img_slice)
        cv2.imwrite(f"{mask_dir}/mask_{count}.png", mask_slice)

        count += 1

    print(f"✅ Saved {count} slices with tumors.")