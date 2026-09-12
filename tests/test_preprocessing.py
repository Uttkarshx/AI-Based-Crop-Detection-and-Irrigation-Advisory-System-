import numpy as np
import pandas as pd
import rasterio
from pathlib import Path

from src.datasets.split import split_by_field
from src.utils.validation import validate_raster, validate_weather


def test_raster_validation(tmp_path: Path):
	profile = {
		"driver": "GTiff",
		"height": 2,
		"width": 2,
		"count": 1,
		"dtype": "float32",
		"crs": "EPSG:4326",
		"transform": rasterio.transform.from_origin(0, 2, 1, 1),
	}
	path = tmp_path / "sample.tif"
	with rasterio.open(path, "w", **profile) as dataset:
		dataset.write(np.ones((1, 2, 2), dtype=np.float32))
	summary = validate_raster(path, include_values=True)
	assert summary["valid_pixels"] == 4


def test_weather_validation():
	frame = pd.DataFrame({
		"date": ["2024-01-02", "2024-01-01"],
		"PRECTOTCORR": [1.0, 0.0],
		"T2M": [20.0, 19.0],
		"RH2M": [50.0, 55.0],
		"WS2M": [2.0, 1.5],
		"ALLSKY_SFC_SW_DWN": [10.0, 11.0],
	})
	assert validate_weather(frame)["duplicate_dates"] == 0


def test_field_split_has_no_overlap():
	frame = pd.DataFrame({"field_id": [f"field_{index}" for index in range(20)]})
	splits = split_by_field(frame, validation_fraction=0.2)
	assert set(splits["train"]["field_id"]).isdisjoint(splits["validation"]["field_id"])
