import pandas as pd

from src.datasets.schema import DatasetSchema, DatasetSchemaError


def validate_dataset(dataframe: pd.DataFrame, task: str | None = None) -> None:
	if dataframe.empty:
		raise DatasetSchemaError("Dataset is empty")
	DatasetSchema.validate(dataframe, task=task)
	if dataframe["field_id"].duplicated().any():
		raise DatasetSchemaError("Dataset contains duplicate field_id values")
	if not dataframe[["latitude", "longitude"]].notna().all().all():
		raise DatasetSchemaError("Dataset contains missing coordinates")
