import pandas as pd
import numpy as np

from src.datasets.schema import DatasetSchema, DatasetSchemaError


def validate_dataset(dataframe: pd.DataFrame, task: str | None = None) -> None:
	if dataframe.empty:
		raise DatasetSchemaError("Dataset is empty")
	DatasetSchema.validate(dataframe, task=task)
	if dataframe["field_id"].duplicated().any():
		raise DatasetSchemaError("Dataset contains duplicate field_id values")
	if not dataframe[["latitude", "longitude"]].notna().all().all():
		raise DatasetSchemaError("Dataset contains missing coordinates")


def validate_crop_classification(
	dataframe: pd.DataFrame,
	crop_mapping: dict[int, str],
) -> None:
	if dataframe.empty:
		raise DatasetSchemaError("Crop dataset is empty")
	required = {
		"state", "field_id", "date", "latitude", "longitude",
		"crop_code", "crop_label", "split",
	}
	missing = sorted(required.difference(dataframe.columns))
	if missing:
		raise DatasetSchemaError(f"Crop dataset is missing columns: {', '.join(missing)}")
	if dataframe["field_id"].isna().any() or dataframe["field_id"].astype(str).str.strip().eq("").any():
		raise DatasetSchemaError("Crop dataset contains invalid field IDs")
	labeled = dataframe.loc[dataframe["split"] != "test"].copy()
	if labeled["crop_code"].isna().any() or labeled["crop_label"].isna().any():
		raise DatasetSchemaError("Crop dataset contains missing crop targets")
	codes = pd.to_numeric(labeled["crop_code"], errors="coerce")
	if codes.isna().any() or not np.equal(codes, codes.astype(int)).all():
		raise DatasetSchemaError("Crop codes must be integer values")
	invalid_codes = sorted(set(codes.astype(int)) - set(crop_mapping))
	if invalid_codes:
		raise DatasetSchemaError(f"Invalid crop codes: {invalid_codes}")
	labels = labeled["crop_label"].astype(str)
	invalid_labels = sorted(set(labels) - set(crop_mapping.values()))
	if invalid_labels:
		raise DatasetSchemaError(f"Invalid crop labels: {invalid_labels}")
	if not (labels == codes.astype(int).map(crop_mapping)).all():
		raise DatasetSchemaError("Crop code and crop label values do not match")
	if set(dataframe["split"].dropna()) - {"train", "validation", "test"}:
		raise DatasetSchemaError("Invalid dataset split")
	if dataframe.duplicated(subset=["field_id"]).any():
		raise DatasetSchemaError("Crop dataset contains duplicate field IDs")
	numeric = dataframe.select_dtypes(include=[np.number])
	if np.isinf(numeric.to_numpy()).any():
		raise DatasetSchemaError("Crop dataset contains infinite feature values")


def validate_split_leakage(frames: dict[str, pd.DataFrame]) -> None:
	sets = {name: set(frame["field_id"]) for name, frame in frames.items()}
	for left, left_ids in sets.items():
		for right, right_ids in sets.items():
			if left < right and left_ids.intersection(right_ids):
				raise DatasetSchemaError(f"Field leakage between {left} and {right}")
