import numpy as np

from src.preprocessing.cloud_mask import mask_invalid


def clean_optical(bands: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
	return {band: mask_invalid(values, 0) for band, values in bands.items()}
