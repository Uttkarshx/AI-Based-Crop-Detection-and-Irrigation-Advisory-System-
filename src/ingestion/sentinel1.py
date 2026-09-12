from pathlib import Path

import numpy as np
import rasterio


def index_sentinel1(root: str | Path) -> dict[str, Path]:
	return {
		path.stem.removeprefix("S1_train_"): path
		for path in Path(root).rglob("S1_*.tif")
		if "field_ids" not in path.stem
	}


def read_sentinel1(path: str | Path) -> dict[str, np.ndarray]:
	with rasterio.open(path) as dataset:
		values = dataset.read(masked=True).filled(np.nan).astype(float)
	return {"vv": values[0], "vh": values[1], "incidence_angle": values[2]}
