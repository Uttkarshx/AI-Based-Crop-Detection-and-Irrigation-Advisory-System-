from pathlib import Path
import re

import numpy as np
import rasterio


def index_ground_truth(root: str | Path, split: str) -> dict[str, Path]:
	result = {}
	for path in (Path(root) / split).glob(f"*labels_{split.removesuffix('_labels')}*.tif"):
		if "field_ids" not in path.stem:
			match = re.search(r"_(?P<field>[0-9a-f]+)$", path.stem)
			if match:
				result[match["field"]] = path
	return result


def index_field_ids(root: str | Path, split: str) -> dict[str, Path]:
	result = {}
	for path in (Path(root) / split).glob("*field_ids.tif"):
		match = re.search(r"_(?P<field>[0-9a-f]+)_field_ids$", path.stem)
		if match:
			result[match["field"]] = path
	return result


def read_label(path: str | Path) -> int | None:
	with rasterio.open(path) as dataset:
		values = dataset.read(1)
	values = values[values > 0]
	if values.size == 0:
		return None
	unique, counts = np.unique(values, return_counts=True)
	return int(unique[np.argmax(counts)])
