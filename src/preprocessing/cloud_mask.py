import numpy as np


def mask_invalid(values: np.ndarray, minimum: float | None = None, maximum: float | None = None) -> np.ndarray:
	result = values.astype(float, copy=True)
	result[~np.isfinite(result)] = np.nan
	if minimum is not None:
		result[result < minimum] = np.nan
	if maximum is not None:
		result[result > maximum] = np.nan
	return result
