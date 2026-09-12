import numpy as np


def summarize_sar(
	vv: np.ndarray,
	vh: np.ndarray,
	incidence_angle: np.ndarray | None = None,
) -> dict[str, float]:
	def mean(values: np.ndarray) -> float:
		valid = values[np.isfinite(values)]
		return float(np.mean(valid)) if valid.size else np.nan

	vv_mean = mean(vv)
	vh_mean = mean(vh)
	with np.errstate(divide="ignore", invalid="ignore"):
		ratio = vh / vv
	return {
		"vv": vv_mean,
		"vh": vh_mean,
		"vh_vv_ratio": mean(ratio),
		"incidence_angle": mean(incidence_angle)
		if incidence_angle is not None
		else np.nan,
	}
