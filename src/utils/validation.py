from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rasterio


class ValidationError(ValueError):
	pass


def validate_raster(path: str | Path, bands: int | None = None, include_values: bool = False) -> dict[str, Any]:
	path = Path(path)
	if not path.is_file():
		raise ValidationError(f"Raster not found: {path}")
	with rasterio.open(path) as dataset:
		if not dataset.crs:
			raise ValidationError(f"Raster has no CRS: {path}")
		if dataset.width < 1 or dataset.height < 1:
			raise ValidationError(f"Raster has invalid dimensions: {path}")
		if bands is not None and dataset.count != bands:
			raise ValidationError(f"Raster has {dataset.count} bands, expected {bands}: {path}")
		if dataset.transform is None or dataset.bounds.left >= dataset.bounds.right or dataset.bounds.bottom >= dataset.bounds.top:
			raise ValidationError(f"Raster has invalid spatial metadata: {path}")
		summary = {
			"path": str(path),
			"width": dataset.width,
			"height": dataset.height,
			"bands": dataset.count,
			"crs": str(dataset.crs),
			"resolution": list(dataset.res),
			"bounds": list(dataset.bounds),
			"dtype": dataset.dtypes[0],
			"nodata": dataset.nodata,
		}
		if include_values:
			values = dataset.read(1, masked=True)
			summary["valid_pixels"] = int(np.ma.count(values))
		return summary


def validate_weather(frame: pd.DataFrame) -> dict[str, Any]:
	required = {"date", "PRECTOTCORR", "T2M", "RH2M", "WS2M", "ALLSKY_SFC_SW_DWN"}
	missing = required.difference(frame.columns)
	if missing:
		raise ValidationError(f"Missing weather columns: {sorted(missing)}")
	dates = pd.to_datetime(frame["date"], errors="coerce")
	if dates.isna().any():
		raise ValidationError("Weather contains invalid dates")
	duplicates = int(dates.duplicated().sum())
	numeric = frame[sorted(required - {"date"})].apply(pd.to_numeric, errors="coerce")
	invalid = int(numeric.isna().sum().sum())
	return {
		"rows": len(frame),
		"date_start": dates.min().date().isoformat(),
		"date_end": dates.max().date().isoformat(),
		"duplicate_dates": duplicates,
		"invalid_numeric_values": invalid,
		"missing_values": int(frame.isna().sum().sum()),
	}


def validate_label_raster(path: str | Path) -> dict[str, Any]:
	summary = validate_raster(path, bands=1)
	with rasterio.open(path) as dataset:
		values = dataset.read(1, masked=True)
		valid = values.compressed()
		if valid.size and not np.equal(valid, valid.astype(np.int64)).all():
			raise ValidationError(f"Label raster contains non-integer values: {path}")
		summary["label_distribution"] = {str(int(value)): int((valid == value).sum()) for value in np.unique(valid)}
	return summary
