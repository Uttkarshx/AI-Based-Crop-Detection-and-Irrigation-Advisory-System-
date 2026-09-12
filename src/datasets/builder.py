from pathlib import Path

import pandas as pd
import json

from src.datasets.split import split_by_field
from src.datasets.validation import validate_crop_classification, validate_dataset, validate_split_leakage


def write_datasets(
	dataframe: pd.DataFrame,
	output_dir: str | Path,
	task: str | None = None,
	validation_fraction: float = 0.2,
) -> dict[str, Path]:
	validate_dataset(dataframe, task=task)
	directory = Path(output_dir)
	directory.mkdir(parents=True, exist_ok=True)
	if "split" in dataframe.columns and (dataframe["split"] == "test").any():
		training = dataframe.loc[dataframe["split"] != "test"].copy()
		test = dataframe.loc[dataframe["split"] == "test"].copy()
		frames = split_by_field(training, validation_fraction)
		frames["test"] = test.reset_index(drop=True)
	else:
		frames = split_by_field(dataframe, validation_fraction)
	paths = {}
	for name, frame in frames.items():
		frame = frame.copy()
		frame["split"] = name
		path = directory / f"{name}.csv"
		frame.to_csv(path, index=False)
		paths[name] = path
	return paths


def write_crop_classification(
	dataframe: pd.DataFrame,
	output_dir: str | Path,
	crop_mapping: dict[int, str],
	validation_fraction: float = 0.2,
) -> dict[str, Path]:
	validate_crop_classification(dataframe, crop_mapping)
	directory = Path(output_dir)
	directory.mkdir(parents=True, exist_ok=True)
	training = dataframe.loc[dataframe["split"] != "test"].copy()
	test = dataframe.loc[dataframe["split"] == "test"].copy()
	frames = split_by_field(training, validation_fraction)
	frames["test"] = test.reset_index(drop=True)
	frames = {name: frame.assign(split=name) for name, frame in frames.items()}
	validate_split_leakage(frames)
	master = pd.concat(frames.values(), ignore_index=True)
	master_path = directory / "master_dataset.csv"
	master.to_csv(master_path, index=False)
	identifier_columns = ["state", "field_id", "date", "latitude", "longitude", "crop_code", "crop_label", "split"]
	optical_columns = [column for column in manifest_columns(master)["optical_only"]]
	sar_columns = [column for column in manifest_columns(master)["sar_only"]]
	base = [column for column in identifier_columns if column in master.columns]
	views = {
		"optical_only.csv": base + optical_columns,
		"sar_only.csv": base + sar_columns,
		"optical_sar.csv": base + optical_columns + sar_columns,
	}
	for filename, columns in views.items():
		master[columns].to_csv(directory / filename, index=False)
	paths = {}
	for name, frame in frames.items():
		path = directory / f"{name}.csv"
		frame.to_csv(path, index=False)
		paths[name] = path
	manifest = {
		"target": ["crop_code", "crop_label"],
		**manifest_columns(master),
		"master_dataset": str(master_path),
		"views": {filename: str(directory / filename) for filename in views},
	}
	(directory / "feature_groups.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
	paths["master_dataset"] = master_path
	paths.update({filename.removesuffix(".csv"): directory / filename for filename in views})
	return paths


def manifest_columns(dataframe: pd.DataFrame) -> dict[str, list[str]]:
	optical = {"coastal", "blue", "green", "red", "red_edge", "red_edge_2", "red_edge_3", "nir", "red_edge_4", "water_vapor", "swir1", "swir2", "ndvi", "evi", "ndwi", "ndmi", "savi"}
	sar = {"vv", "vh", "vh_vv_ratio", "incidence_angle"}
	return {
		"optical_only": [column for column in dataframe.columns if column in optical],
		"sar_only": [column for column in dataframe.columns if column in sar],
		"soil": [column for column in dataframe.columns if column.startswith("soil_") and column not in {"soil_moisture_percent", "soil_temperature_percent", "soil_temperature_celsius", "soil_type"}],
		"weather": [column for column in dataframe.columns if column in {"rainfall_mm", "temperature_celsius", "humidity_percent", "wind_speed_ms", "solar_radiation_mj_m2"}],
	}
