import cv2
import numpy as np
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

print("Loading model...")
model = load_model("model/unet_model.h5")

# Change index if needed
img_path = "data/processed/images/img_0.png"

print("Loading image...")
img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

if img is None:
    print("❌ Image not found. Check path.")
    exit()

img = cv2.resize(img, (128, 128))
img = img / 255.0
img = img.reshape(1, 128, 128, 1)

print("Predicting...")
pred = model.predict(img)[0]

# Show results
plt.figure(figsize=(8,4))

plt.subplot(1,2,1)
plt.title("Input MRI")
plt.imshow(img[0,:,:,0], cmap='gray')
plt.axis('off')

plt.subplot(1,2,2)
plt.title("Predicted Tumor")
plt.imshow(pred[:,:,0], cmap='gray')
plt.axis('off')

plt.show()