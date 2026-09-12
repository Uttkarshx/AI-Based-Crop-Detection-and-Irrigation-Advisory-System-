import numpy as np

from src.preprocessing.cloud_mask import mask_invalid


def clean_sar(bands: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
	result = {band: mask_invalid(values) for band, values in bands.items()}
	if "incidence_angle" in result:
		result["incidence_angle"] = mask_invalid(result["incidence_angle"], 0, 90)
	return result
