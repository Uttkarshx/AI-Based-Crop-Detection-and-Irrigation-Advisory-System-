import numpy as np


def summarize_temporal(ndvi_values: list[float]) -> dict[str, float]:
	values = np.asarray(ndvi_values, dtype=float)
	values = values[np.isfinite(values)]
	if values.size == 0:
		return {
			"ndvi_change": np.nan,
			"ndvi_mean": np.nan,
			"ndvi_std": np.nan,
			"vegetation_anomaly": np.nan,
		}
	mean = float(np.mean(values))
	return {
		"ndvi_change": float(values[-1] - values[0]),
		"ndvi_mean": mean,
		"ndvi_std": float(np.std(values)),
		"vegetation_anomaly": float(values[-1] - mean),
	}
