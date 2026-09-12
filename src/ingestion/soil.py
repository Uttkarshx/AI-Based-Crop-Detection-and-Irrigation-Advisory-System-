import re
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform


def index_soil(root: str | Path) -> dict[str, list[Path]]:
	result: dict[str, list[Path]] = {}
	pattern = re.compile(r"soilgrids_(?P<state>[a-z_]+)_(?P<property>[a-z0-9]+)_(?P<depth>[0-9-]+cm)_mean")
	for path in Path(root).rglob("*.tif"):
		match = pattern.search(path.stem)
		if match:
			result.setdefault(match["state"], []).append(path)
	return result


def sample_soil(paths: list[Path], longitude: float, latitude: float) -> dict[str, float]:
	result: dict[str, float] = {}
	for path in paths:
		with rasterio.open(path) as dataset:
			x, y = transform("EPSG:4326", dataset.crs, [longitude], [latitude])
			if not (dataset.bounds.left <= x[0] <= dataset.bounds.right and dataset.bounds.bottom <= y[0] <= dataset.bounds.top):
				continue
			value = next(dataset.sample([(x[0], y[0])]))[0]
			if dataset.nodata is not None and value == dataset.nodata:
				continue
			match = re.search(r"soilgrids_[a-z_]+_([a-z0-9]+)_([0-9-]+cm)_mean", path.stem)
			if match:
				result[f"soil_{match[1]}_{match[2]}"] = float(value)
	return result
