import hashlib

import pandas as pd


def split_by_field(
	dataframe: pd.DataFrame,
	validation_fraction: float = 0.2,
	test_fraction: float = 0.0,
) -> dict[str, pd.DataFrame]:
	if not 0 <= validation_fraction < 1 or not 0 <= test_fraction < 1:
		raise ValueError("Split fractions must be between 0 and 1")
	if validation_fraction + test_fraction >= 1:
		raise ValueError("Validation and test fractions must sum to less than 1")
	def bucket(field_id: str) -> float:
		value = hashlib.sha256(field_id.encode()).hexdigest()[:12]
		return int(value, 16) / int("f" * 12, 16)
	values = dataframe["field_id"].astype(str).map(bucket)
	test = dataframe.loc[values < test_fraction]
	validation = dataframe.loc[(values >= test_fraction) & (values < test_fraction + validation_fraction)]
	train = dataframe.loc[values >= test_fraction + validation_fraction]
	return {"train": train.reset_index(drop=True), "validation": validation.reset_index(drop=True), "test": test.reset_index(drop=True)}
