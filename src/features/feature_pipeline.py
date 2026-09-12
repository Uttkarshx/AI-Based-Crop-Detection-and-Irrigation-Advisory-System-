from typing import Any

import numpy as np

from src.features.sar_features import summarize_sar
from src.features.spectral import summarize_bands
from src.features.temporal import summarize_temporal
from src.features.vegetation_indices import calculate_indices


def build_features(
	optical: dict[str, np.ndarray],
	sar: dict[str, np.ndarray],
	temporal_ndvi: list[float] | None = None,
) -> dict[str, Any]:
	optical_features = summarize_bands(optical)
	indices = calculate_indices(
		red=optical["B04"],
		nir=optical["B08"],
		blue=optical["B02"],
		green=optical["B03"],
		swir1=optical["B11"],
	)
	result = {
		**optical_features,
		**{name: float(np.nanmean(values)) for name, values in indices.items()},
		**summarize_sar(sar["vv"], sar["vh"], sar.get("incidence_angle")),
		**summarize_temporal(temporal_ndvi or [float(np.nanmean(indices["ndvi"]))]),
	}
	return result
