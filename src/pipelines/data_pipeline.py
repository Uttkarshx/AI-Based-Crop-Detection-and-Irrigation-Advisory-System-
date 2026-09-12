import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import rasterio
from rasterio.warp import transform

from src.datasets.builder import write_crop_classification
from src.features.feature_pipeline import build_features
from src.ingestion.ground_truth import index_field_ids, index_ground_truth, read_label
from src.ingestion.sentinel1 import index_sentinel1, read_sentinel1
from src.ingestion.sentinel2 import index_sentinel2, read_sentinel2
from src.ingestion.soil import index_soil, sample_soil
from src.ingestion.weather import load_weather
from src.preprocessing.optical import clean_optical
from src.preprocessing.sar import clean_sar
from src.preprocessing.spatial_alignment import align_array
from src.utils.config import ConfigLoader
from src.utils.logging import configure_logging
from src.utils.validation import ValidationError, validate_label_raster, validate_raster, validate_weather


def _quality_report(report: dict[str, Any], output_dir: Path) -> None:
	report_dir = Path("outputs/reports")
	report_dir.mkdir(parents=True, exist_ok=True)
	report["completed_at"] = datetime.now(timezone.utc).isoformat()
	json_path = report_dir / "data_quality.json"
	json_path.write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
	lines = ["# Data Quality Report", "", f"Completed: {report['completed_at']}", ""]
	for key, value in report.items():
		if key != "completed_at":
			lines.append(f"- {key}: {json.dumps(value, default=str)}")
	(report_dir / "data_quality.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _feature_report(dataframe: pd.DataFrame, output_dir: Path) -> None:
	report_dir = Path("outputs/reports")
	report_dir.mkdir(parents=True, exist_ok=True)
	feature_groups = {
		"Sentinel-2": [column for column in dataframe.columns if column in {"coastal", "blue", "green", "red", "red_edge", "red_edge_2", "red_edge_3", "nir", "red_edge_4", "water_vapor", "swir1", "swir2", "ndvi", "evi", "ndwi", "ndmi", "savi"}],
		"Sentinel-1": [column for column in dataframe.columns if column in {"vv", "vh", "vh_vv_ratio", "incidence_angle"}],
		"Soil": [column for column in dataframe.columns if column.startswith("soil_") and column not in {"soil_moisture_percent", "soil_temperature_celsius", "soil_type"}],
		"Weather": [column for column in dataframe.columns if column in {"rainfall_mm", "temperature_celsius", "humidity_percent", "wind_speed_ms", "solar_radiation_mj_m2"}],
	}
	feature_columns = [column for columns in feature_groups.values() for column in columns]
	class_distribution = dataframe.loc[dataframe["crop_label"].notna()].groupby(["crop_code", "crop_label"]).field_id.nunique().to_dict()
	missing = {column: int(value) for column, value in dataframe[feature_columns + ["crop_code", "crop_label"]].isna().sum().items() if value}
	lines = [
		"# Feature Extraction Report",
		"",
		f"- Total samples: {len(dataframe)}",
		f"- Total fields: {dataframe['field_id'].nunique()}",
		f"- States: {', '.join(sorted(dataframe['state'].dropna().unique()))}",
		f"- Feature count: {len(feature_columns)}",
		f"- Split counts: {dataframe['split'].value_counts().to_dict()}",
		f"- Class distribution by field: {class_distribution}",
		f"- Missing feature/target values: {missing}",
		f"- Duplicate rows: {int(dataframe.duplicated().sum())}",
		"",
		"## Feature Groups",
		"",
	]
	for name, columns in feature_groups.items():
		lines.append(f"- {name} ({len(columns)}): {', '.join(columns)}")
	lines.extend([
		"",
		"## Outputs",
		"",
		f"- Master: {output_dir / 'master_dataset.csv'}",
		f"- Optical-only: {output_dir / 'optical_only.csv'}",
		f"- SAR-only: {output_dir / 'sar_only.csv'}",
		f"- Optical+SAR: {output_dir / 'optical_sar.csv'}",
	])
	(report_dir / "feature_extraction_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _discover_and_validate(root: Path, logger: Any) -> dict[str, Any]:
	s1_files = list((root / "sentinel1").rglob("*.tif"))
	s2_files = list((root / "sentinel2").rglob("*.tif"))
	soil_files = list((root / "soil").rglob("*.tif"))
	train_files = list((root / "ground_truth" / "train_labels").glob("*.tif"))
	test_files = list((root / "ground_truth" / "test_labels").glob("*.tif"))
	weather_files = list((root / "meteorological" / "nasa_power").glob("*.csv"))
	required = {"sentinel1": s1_files, "sentinel2": s2_files, "soil": soil_files, "weather": weather_files, "ground_truth": train_files + test_files}
	missing = [name for name, files in required.items() if not files]
	if missing:
		raise FileNotFoundError(f"Required datasets are missing: {', '.join(missing)}")
	failures = []
	raster_samples = []
	for path in s1_files + s2_files + soil_files:
		try:
			metadata = validate_raster(path, include_values=len(raster_samples) < 20)
			if len(raster_samples) < 20:
				raster_samples.append(metadata)
		except (OSError, ValidationError) as exc:
			failures.append({"path": str(path), "error": str(exc)})
	label_samples = []
	for path in train_files + test_files:
		if "field_ids" not in path.name:
			try:
				if len(label_samples) < 20:
					label_samples.append(validate_label_raster(path))
			except (OSError, ValidationError) as exc:
				failures.append({"path": str(path), "error": str(exc)})
	weather_reports = []
	for path in weather_files:
		try:
			weather_reports.append({"path": str(path), **validate_weather(pd.read_csv(path))})
		except (OSError, ValueError, ValidationError) as exc:
			failures.append({"path": str(path), "error": str(exc)})
	logger.info("discovered sentinel1=%s sentinel2=%s soil=%s weather=%s train_labels=%s test_labels=%s", len(s1_files), len(s2_files), len(soil_files), len(weather_files), len(train_files), len(test_files))
	return {
		"discovered_files": {name: len(files) for name, files in required.items()},
		"processed_files": {"raster_metadata": len(s1_files) + len(s2_files) + len(soil_files), "label_metadata": len(train_files) + len(test_files), "weather": len(weather_reports)},
		"failed_files": failures,
		"raster_samples": raster_samples,
		"label_samples": label_samples,
		"weather": weather_reports,
	}


def _aligned(path: Path, reference: dict[str, Any], categorical: bool = False) -> np.ndarray:
	with rasterio.open(path) as dataset:
		values = dataset.read(1, masked=True).astype(float).filled(np.nan)
		if (
			values.shape == reference["shape"]
			and dataset.transform == reference["transform"]
			and dataset.crs == reference["crs"]
		):
			return values
		return align_array(
			values,
			dataset.transform,
			dataset.crs,
			reference["shape"],
			reference["transform"],
			reference["crs"],
			categorical=categorical,
		)


def _aligned_band(path: Path, band: int, reference: dict[str, Any]) -> np.ndarray:
	with rasterio.open(path) as dataset:
		values = dataset.read(band, masked=True).astype(float).filled(np.nan)
		if (
			values.shape == reference["shape"]
			and dataset.transform == reference["transform"]
			and dataset.crs == reference["crs"]
		):
			return values
		return align_array(
			values,
			dataset.transform,
			dataset.crs,
			reference["shape"],
			reference["transform"],
			reference["crs"],
		)


def _reference(path: Path) -> dict[str, Any]:
	with rasterio.open(path) as dataset:
		return {
			"shape": (dataset.height, dataset.width),
			"transform": dataset.transform,
			"crs": dataset.crs,
			"longitude": dataset.xy(dataset.height // 2, dataset.width // 2)[0],
			"latitude": dataset.xy(dataset.height // 2, dataset.width // 2)[1],
		}


def _coordinates(reference: dict[str, Any]) -> tuple[float, float]:
	longitude, latitude = transform(
		reference["crs"], "EPSG:4326", [reference["longitude"]], [reference["latitude"]]
	)
	return float(latitude[0]), float(longitude[0])


def _state_for(loader: ConfigLoader, latitude: float, longitude: float) -> str | None:
	for path in sorted((loader.config_dir / "study_areas").glob("*.yaml")):
		identifier = path.stem
		if identifier == "custom_area":
			continue
		area = loader.load_study_area(identifier)["study_area"]
		bounds = area.get("bounds", {})
		if (
			bounds.get("min_latitude", -90) <= latitude <= bounds.get("max_latitude", 90)
			and bounds.get("min_longitude", -180) <= longitude <= bounds.get("max_longitude", 180)
		):
			return identifier
	return None


def _record(
	field_id: str,
	split: str,
	target_path: Path | None,
	s1_path: Path | None,
	s2_paths: dict[str, Path],
	soil_paths: dict[str, list[Path]],
	loader: ConfigLoader,
	weather_root: Path,
	label_mapping: dict[int, str],
) -> dict[str, Any] | None:
	reference_path = target_path or next(iter(s2_paths.values()))
	reference = _reference(reference_path)
	latitude, longitude = _coordinates(reference)
	state = _state_for(loader, latitude, longitude)
	if state is None:
		return None
	optical = clean_optical({
		band: _aligned(path, reference)
		for band, path in s2_paths.items()
	})
	if s1_path:
		sar = clean_sar({
			"vv": _aligned_band(s1_path, 1, reference),
			"vh": _aligned_band(s1_path, 2, reference),
			"incidence_angle": _aligned_band(s1_path, 3, reference),
		})
	else:
		missing = np.full(reference["shape"], np.nan, dtype=float)
		sar = {"vv": missing, "vh": missing, "incidence_angle": missing}
	feature_values = build_features(optical, sar)
	weather = load_weather(weather_root, state)
	soil = sample_soil(soil_paths.get(state, []), longitude, latitude)
	record = {
		"field_id": field_id,
		"date": weather.get("date"),
		"latitude": latitude,
		"longitude": longitude,
		"crop_code": read_label(target_path) if target_path else None,
		"crop_label": None,
		"growth_stage_label": None,
		"stress_label": None,
		"soil_moisture_percent": np.nan,
		"soil_temperature_celsius": np.nan,
		"soil_type": "unknown",
		**feature_values,
		**weather,
		**soil,
		"state": state,
		"split": split,
	}
	crop_code = record["crop_code"]
	if crop_code is not None:
		if crop_code not in label_mapping:
			raise ValueError(f"Unsupported AgriFieldNet crop code: {crop_code}")
		record["crop_label"] = label_mapping[crop_code]
	return record


def build_dataset(
	config_dir: str | Path = "configs",
	data_dir: str | Path = "data/raw",
	output_dir: str | Path = "data/processed",
	label_mapping: dict[int, str] | None = None,
	limit: int | None = None,
) -> dict[str, Path]:
	root = Path(data_dir)
	loader = ConfigLoader(config_dir)
	logger = configure_logging("INFO")
	logger.info("starting data preprocessing")
	report = _discover_and_validate(root, logger)
	s1 = index_sentinel1(root / "sentinel1")
	s2 = index_sentinel2(root / "sentinel2")
	train_labels = index_ground_truth(root / "ground_truth", "train_labels")
	test_ids = index_field_ids(root / "ground_truth", "test_labels")
	soil = index_soil(root / "soil")
	soil = {
		state: [
			path for path in paths
			if any(f"_{property_name}_0-5cm_" in path.name for property_name in ("clay", "sand", "silt", "soc", "phh2o"))
		]
		for state, paths in soil.items()
	}
	fields = [(field_id, "train", train_labels[field_id]) for field_id in sorted(train_labels) if field_id in s1 and field_id in s2]
	fields += [
		(field_id, "test", None)
		for field_id in sorted(test_ids)
		if field_id in s2 and field_id not in train_labels
	]
	if limit is not None:
		fields = fields[:limit]
	records = []
	configured_classes = loader.load_crop("default")["crop"]["classes"]
	mapping = label_mapping or {int(item["code"]): item["name"] for item in configured_classes}
	for field_id, split, target in fields:
		record = _record(field_id, split, target, s1.get(field_id), s2[field_id], soil, loader, root / "meteorological" / "nasa_power", mapping)
		if record:
			records.append(record)
	dataframe = pd.DataFrame(records)
	final_dir = Path(output_dir)
	if final_dir.name != "crop_classification":
		final_dir = final_dir / "crop_classification"
	paths = write_crop_classification(dataframe, final_dir, mapping)
	master = pd.read_csv(paths["master_dataset"])
	_feature_report(master, final_dir)
	report["dataset"] = {"rows": len(dataframe), "columns": len(dataframe.columns), "output_files": {name: str(path) for name, path in paths.items()}}
	report["missing_values"] = {column: int(value) for column, value in dataframe.isna().sum().items() if value}
	report["records_skipped"] = len(fields) - len(dataframe)
	_quality_report(report, Path(output_dir))
	logger.info("completed data preprocessing rows=%s outputs=%s", len(dataframe), paths)
	return paths


def main() -> None:
	parser = argparse.ArgumentParser()
	parser.add_argument("--config-dir", default="configs")
	parser.add_argument("--data-dir", default="data/raw")
	parser.add_argument("--output-dir", default="data/processed/crop_classification")
	parser.add_argument("--label-mapping")
	parser.add_argument("--limit", type=int)
	arguments = parser.parse_args()
	mapping = json.loads(Path(arguments.label_mapping).read_text()) if arguments.label_mapping else None
	build_dataset(arguments.config_dir, arguments.data_dir, arguments.output_dir, mapping, arguments.limit)


if __name__ == "__main__":
	main()
