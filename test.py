print("STARTING PROGRAM...")

from utils.preprocess import load_mri, normalize
import matplotlib.pyplot as plt

img_path = "data/raw/BraTS20_Training_001/BraTS20_Training_001_flair.nii"
mask_path = "data/raw/BraTS20_Training_001/BraTS20_Training_001_seg.nii"

print("Loading image...")

image = load_mri(img_path)
image = normalize(image)

mask = load_mri(mask_path)

print("Image Shape:", image.shape)
print("Mask Shape:", mask.shape)

print("Showing images...")

plt.imshow(image[:, :, 80], cmap='gray')
plt.title("MRI Image")
plt.axis('off')
plt.show()

plt.imshow(mask[:, :, 80])
plt.title("Tumor Mask")
plt.axis('off')
plt.show()