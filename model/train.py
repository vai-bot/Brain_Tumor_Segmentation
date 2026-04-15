import os
import cv2
import numpy as np
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.losses import BinaryCrossentropy
from model.unet import build_unet

# Load data
def load_data(img_dir, mask_dir):
    images = []
    masks = []

    img_files = sorted(os.listdir(img_dir))
    mask_files = sorted(os.listdir(mask_dir))

    for img_file, mask_file in zip(img_files, mask_files):
        img = cv2.imread(os.path.join(img_dir, img_file), cv2.IMREAD_GRAYSCALE)
        mask = cv2.imread(os.path.join(mask_dir, mask_file), cv2.IMREAD_GRAYSCALE)

        img = img / 255.0
        mask = mask / 255.0

        images.append(img)
        masks.append(mask)

    images = np.array(images).reshape(-1,128,128,1)
    masks = np.array(masks).reshape(-1,128,128,1)

    return images, masks


# Paths
img_dir = "data/processed/images"
mask_dir = "data/processed/masks"

X, y = load_data(img_dir, mask_dir)

print("Dataset Loaded:", X.shape)

# Build model
model = build_unet()

model.compile(
    optimizer=Adam(),
    loss=BinaryCrossentropy(),
    metrics=["accuracy"]
)

# Train
model.fit(X, y, epochs=5, batch_size=4)

# Save model
model.save("model/unet_model.h5")

print("✅ Model trained and saved!")