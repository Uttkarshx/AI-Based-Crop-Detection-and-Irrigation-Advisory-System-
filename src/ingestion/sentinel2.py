import re
from pathlib import Path

import numpy as np
import rasterio


def index_sentinel2(root: str | Path) -> dict[str, dict[str, Path]]:
	result: dict[str, dict[str, Path]] = {}
	pattern = re.compile(r"source_(?P<field>[0-9a-f]+)_(?P<band>B(?:0[1-9]|1[12]|8A))_10m")
	for path in Path(root).rglob("*.tif"):
		match = pattern.search(path.name)
		if match:
			result.setdefault(match["field"], {})[match["band"]] = path
	return result


def read_sentinel2(paths: dict[str, Path]) -> dict[str, np.ndarray]:
	values = {}
	for band, path in paths.items():
		with rasterio.open(path) as dataset:
			masked = dataset.read(1, masked=True)
			values[band] = masked.astype(float).filled(np.nan)
	return values
