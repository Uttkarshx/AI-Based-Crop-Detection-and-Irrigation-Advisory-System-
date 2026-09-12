import numpy as np


def _ratio(numerator: np.ndarray, denominator: np.ndarray) -> np.ndarray:
	with np.errstate(divide="ignore", invalid="ignore"):
		result = numerator / denominator
	return np.where(np.isfinite(result), result, np.nan)


def calculate_indices(
	red: np.ndarray,
	nir: np.ndarray,
	blue: np.ndarray,
	green: np.ndarray,
	swir1: np.ndarray,
) -> dict[str, np.ndarray]:
	ndvi = _ratio(nir - red, nir + red)
	return {
		"ndvi": ndvi,
		"evi": 2.5 * _ratio(nir - red, nir + 6 * red - 7.5 * blue + 1),
		"ndwi": _ratio(green - nir, green + nir),
		"ndmi": _ratio(nir - swir1, nir + swir1),
		"savi": 1.5 * _ratio(nir - red, nir + red + 0.5),
	}
