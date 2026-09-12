import numpy as np


BAND_NAMES = {
	"B01": "coastal",
	"B02": "blue",
	"B03": "green",
	"B04": "red",
	"B05": "red_edge",
	"B06": "red_edge_2",
	"B07": "red_edge_3",
	"B08": "nir",
	"B8A": "red_edge_4",
	"B09": "water_vapor",
	"B11": "swir1",
	"B12": "swir2",
}


def summarize_bands(bands: dict[str, np.ndarray]) -> dict[str, float]:
	result = {}
	for band, values in bands.items():
		valid = values[np.isfinite(values)]
		result[BAND_NAMES.get(band, band.lower())] = (
			float(np.mean(valid)) if valid.size else np.nan
		)
	return result
