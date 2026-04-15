from utils.preprocess import load_mri, save_slices

img_path = "data/raw/BraTS20_Training_001/BraTS20_Training_001_flair.nii"
mask_path = "data/raw/BraTS20_Training_001/BraTS20_Training_001_seg.nii"

image = load_mri(img_path)
mask = load_mri(mask_path)

save_slices(image, mask)