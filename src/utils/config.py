from pathlib import Path
from typing import Any

import yaml


class ConfigurationError(Exception):
    """Raised when configuration loading or validation fails."""


class ConfigLoader:
    """Loads and manages project YAML configuration."""

    SUPPORTED_ENVIRONMENTS = {"development", "production"}

    def __init__(self, config_dir: str | Path = "configs") -> None:
        self.config_dir = Path(config_dir)

        if not self.config_dir.exists():
            raise ConfigurationError(
                f"Configuration directory not found: {self.config_dir}"
            )

    def load_yaml(self, file_path: str | Path) -> dict[str, Any]:
        """Load a YAML configuration file."""

        path = Path(file_path)

        if not path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {path}"
            )

        try:
            with path.open("r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

        except yaml.YAMLError as exc:
            raise ConfigurationError(
                f"Invalid YAML in configuration file: {path}"
            ) from exc

        if data is None:
            return {}

        if not isinstance(data, dict):
            raise ConfigurationError(
                f"Configuration root must be a mapping: {path}"
            )

        return data

    def load_base(self) -> dict[str, Any]:
        """Load the base configuration."""

        return self.load_yaml(
            self.config_dir / "base.yaml"
        )

    def load_environment(
        self,
        environment: str,
    ) -> dict[str, Any]:
        """Load environment-specific configuration."""

        if environment not in self.SUPPORTED_ENVIRONMENTS:
            raise ConfigurationError(
                f"Unsupported environment: {environment}"
            )

        return self.load_yaml(
            self.config_dir / f"{environment}.yaml"
        )

    def _load_named(
        self,
        directory: str,
        identifier: str,
        section: str,
    ) -> dict[str, Any]:
        """Load and validate a named configuration file."""

        if not identifier or Path(identifier).name != identifier:
            raise ConfigurationError(
                f"Invalid {section} identifier: {identifier}"
            )

        config = self.load_yaml(
            self.config_dir / directory / f"{identifier}.yaml"
        )

        if section not in config or not isinstance(config[section], dict):
            raise ConfigurationError(
                f"Missing '{section}' section in {directory}/{identifier}.yaml"
            )

        configured_name = config[section].get("name")
        if configured_name != identifier:
            raise ConfigurationError(
                f"{section.title()} name '{configured_name}' does not match "
                f"identifier '{identifier}'"
            )

        return config

    def load_study_area(self, study_area: str) -> dict[str, Any]:
        """Load a study-area configuration by identifier."""

        return self._load_named("study_areas", study_area, "study_area")

    def load_crop(self, crop: str) -> dict[str, Any]:
        """Load a crop configuration by identifier."""

        return self._load_named("crops", crop, "crop")

    def load_model(self, model: str) -> dict[str, Any]:
        """Load a model configuration by identifier."""

        return self._load_named("models", model, "model")

    @staticmethod
    def merge(
        base: dict[str, Any],
        override: dict[str, Any],
    ) -> dict[str, Any]:
        """Recursively merge two configuration dictionaries."""

        result = base.copy()

        for key, value in override.items():

            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = ConfigLoader.merge(
                    result[key],
                    value,
                )
            else:
                result[key] = value

        return result

    def load(
        self,
        environment: str = "development",
        study_area: str | None = None,
        crop: str | None = None,
        model: str | None = None,
    ) -> dict[str, Any]:
        """Load base, environment, and optional named configurations."""

        config = self.merge(
            self.load_base(),
            self.load_environment(environment),
        )

        named_configs = (
            (study_area, self.load_study_area),
            (crop, self.load_crop),
            (model, self.load_model),
        )
        for identifier, loader in named_configs:
            if identifier is not None:
                config = self.merge(config, loader(identifier))

        return config