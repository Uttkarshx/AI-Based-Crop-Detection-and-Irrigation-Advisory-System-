from pathlib import Path

import pandas as pd

from src.datasets.split import split_by_field
from src.datasets.validation import validate_dataset


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
		path = directory / f"{name}.csv"
		frame.to_csv(path, index=False)
		paths[name] = path
	return paths
