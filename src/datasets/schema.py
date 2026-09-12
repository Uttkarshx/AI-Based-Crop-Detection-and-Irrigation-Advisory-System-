"""
Dataset schema definitions for the crop monitoring and irrigation project.

This module defines:
- Common dataset columns
- Satellite feature columns
- Meteorological and soil columns
- ML target columns
- Required columns for each ML task
- Basic DataFrame schema validation
"""

from dataclasses import dataclass
from typing import ClassVar

import pandas as pd


class DatasetSchemaError(Exception):
    """Raised when a dataset does not follow the expected schema."""


@dataclass(frozen=True)
class ColumnDefinition:
    """Definition of a single dataset column."""

    name: str
    description: str
    required: bool = True


class DatasetSchema:
    """
    Central schema definition for the project dataset.

    The schema supports three ML tasks:

    1. Crop classification
    2. Growth-stage classification
    3. Moisture-stress detection
    """

    # ------------------------------------------------------------------
    # IDENTIFICATION / SPATIAL / TEMPORAL COLUMNS
    # ------------------------------------------------------------------

    IDENTIFICATION_COLUMNS: ClassVar[tuple[str, ...]] = (
        "field_id",
        "date",
        "latitude",
        "longitude",
    )

    # ------------------------------------------------------------------
    # SENTINEL-2 / OPTICAL FEATURES
    # ------------------------------------------------------------------

    OPTICAL_FEATURES: ClassVar[tuple[str, ...]] = (
        "blue",
        "green",
        "red",
        "nir",
        "red_edge",
        "swir1",
        "swir2",
    )

    # ------------------------------------------------------------------
    # VEGETATION / SPECTRAL INDICES
    # ------------------------------------------------------------------

    VEGETATION_FEATURES: ClassVar[tuple[str, ...]] = (
        "ndvi",
        "evi",
        "ndwi",
        "ndmi",
        "savi",
    )

    # ------------------------------------------------------------------
    # SENTINEL-1 / SAR FEATURES
    # ------------------------------------------------------------------

    SAR_FEATURES: ClassVar[tuple[str, ...]] = (
        "vv",
        "vh",
        "vh_vv_ratio",
    )

    # ------------------------------------------------------------------
    # TEMPORAL / PHENOLOGICAL FEATURES
    # ------------------------------------------------------------------

    TEMPORAL_FEATURES: ClassVar[tuple[str, ...]] = (
        "ndvi_change",
        "ndvi_mean",
        "ndvi_std",
        "vegetation_anomaly",
    )

    # ------------------------------------------------------------------
    # METEOROLOGICAL FEATURES
    # ------------------------------------------------------------------

    METEOROLOGICAL_FEATURES: ClassVar[tuple[str, ...]] = (
        "rainfall_mm",
        "et0_mm",
        "temperature_celsius",
        "humidity_percent",
    )

    # ------------------------------------------------------------------
    # SOIL FEATURES
    # ------------------------------------------------------------------

    SOIL_FEATURES: ClassVar[tuple[str, ...]] = (
        "soil_moisture_percent",
        "soil_temperature_celsius",
        "soil_type",
    )

    SOIL_SOURCE_FEATURES: ClassVar[tuple[str, ...]] = (
        "soil_clay_0-5cm",
        "soil_sand_0-5cm",
        "soil_silt_0-5cm",
        "soil_soc_0-5cm",
        "soil_phh2o_0-5cm",
    )

    # ------------------------------------------------------------------
    # ML TARGET LABELS
    # ------------------------------------------------------------------

    TARGET_COLUMNS: ClassVar[tuple[str, ...]] = (
        "crop_label",
        "growth_stage_label",
        "stress_label",
    )

    # ------------------------------------------------------------------
    # ALL FEATURE COLUMNS
    # ------------------------------------------------------------------

    FEATURE_COLUMNS: ClassVar[tuple[str, ...]] = (
        OPTICAL_FEATURES
        + VEGETATION_FEATURES
        + SAR_FEATURES
        + TEMPORAL_FEATURES
        + METEOROLOGICAL_FEATURES
        + SOIL_FEATURES
    )

    # ------------------------------------------------------------------
    # TASK DEFINITIONS
    # ------------------------------------------------------------------

    TASK_TARGETS: ClassVar[dict[str, str]] = {
        "crop_classification": "crop_label",
        "growth_stage_classification": "growth_stage_label",
        "stress_detection": "stress_label",
    }

    # ------------------------------------------------------------------
    # VALID VALUES
    # ------------------------------------------------------------------

    SUPPORTED_CROPS: ClassVar[tuple[str, ...]] = (
        "wheat",
        "mustard",
        "lentil",
        "fallow",
        "green_pea",
        "sugarcane",
        "garlic",
        "maize",
        "gram",
        "coriander",
        "potato",
        "bersem",
        "rice",
    )

    SUPPORTED_GROWTH_STAGES: ClassVar[tuple[str, ...]] = (
        "germination",
        "vegetative",
        "reproductive",
        "maturity",
    )

    SUPPORTED_STRESS_CLASSES: ClassVar[tuple[str, ...]] = (
        "healthy",
        "stressed",
    )

    # ------------------------------------------------------------------
    # PUBLIC METHODS
    # ------------------------------------------------------------------

    @classmethod
    def get_target_column(cls, task: str) -> str:
        """
        Return the target column associated with an ML task.

        Example:
            DatasetSchema.get_target_column("crop_classification")
            -> "crop_label"
        """

        if task not in cls.TASK_TARGETS:
            supported_tasks = ", ".join(cls.TASK_TARGETS.keys())

            raise DatasetSchemaError(
                f"Unsupported task '{task}'. "
                f"Supported tasks: {supported_tasks}"
            )

        return cls.TASK_TARGETS[task]

    @classmethod
    def get_required_columns(cls, task: str) -> list[str]:
        """
        Return the columns required to train a particular ML task.

        Identification columns + all feature columns + task target.
        """

        target_column = cls.get_target_column(task)

        return [
            *cls.IDENTIFICATION_COLUMNS,
            *cls.FEATURE_COLUMNS,
            target_column,
        ]

    @classmethod
    def get_feature_columns(cls) -> list[str]:
        """Return all model input feature columns."""

        return list(cls.FEATURE_COLUMNS)

    @classmethod
    def get_target_columns(cls) -> list[str]:
        """Return all available ML target columns."""

        return list(cls.TARGET_COLUMNS)

    @classmethod
    def validate_columns(
        cls,
        dataframe: pd.DataFrame,
        task: str | None = None,
    ) -> None:
        """
        Validate whether the DataFrame contains the expected columns.

        If a task is provided, its target column is also required.
        """

        if not isinstance(dataframe, pd.DataFrame):
            raise DatasetSchemaError(
                "Input dataset must be a pandas DataFrame."
            )

        if task is not None:
            required_columns = cls.get_required_columns(task)
        else:
            required_columns = [
                *cls.IDENTIFICATION_COLUMNS,
                *cls.FEATURE_COLUMNS,
            ]

        missing_columns = [
            column
            for column in required_columns
            if column not in dataframe.columns
        ]

        if missing_columns:
            raise DatasetSchemaError(
                "Dataset is missing required columns: "
                + ", ".join(missing_columns)
            )

    @classmethod
    def validate_targets(
        cls,
        dataframe: pd.DataFrame,
        task: str,
    ) -> None:
        """
        Validate target labels for a specific ML task.
        """

        target_column = cls.get_target_column(task)

        if target_column not in dataframe.columns:
            raise DatasetSchemaError(
                f"Target column '{target_column}' "
                f"not found in dataset."
            )

        # Remove missing values before checking unique labels.
        values = (
            dataframe[target_column]
            .dropna()
            .astype(str)
            .str.lower()
            .unique()
        )

        if task == "crop_classification":
            allowed_values = set(cls.SUPPORTED_CROPS)

        elif task == "growth_stage_classification":
            allowed_values = set(cls.SUPPORTED_GROWTH_STAGES)

        elif task == "stress_detection":
            allowed_values = set(cls.SUPPORTED_STRESS_CLASSES)

        else:
            raise DatasetSchemaError(
                f"Unsupported task '{task}'."
            )

        invalid_values = [
            value
            for value in values
            if value not in allowed_values
        ]

        if invalid_values:
            raise DatasetSchemaError(
                f"Invalid labels found in '{target_column}': "
                + ", ".join(invalid_values)
            )

    @classmethod
    def validate(
        cls,
        dataframe: pd.DataFrame,
        task: str | None = None,
    ) -> None:
        """
        Perform complete basic schema validation.

        Checks:
        - DataFrame type
        - Required columns
        - Target labels when a task is supplied
        """

        cls.validate_columns(
            dataframe=dataframe,
            task=task,
        )

        if task is not None:
            cls.validate_targets(
                dataframe=dataframe,
                task=task,
            )