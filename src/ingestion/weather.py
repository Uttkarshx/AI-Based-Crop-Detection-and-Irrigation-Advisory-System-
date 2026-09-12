from pathlib import Path

import pandas as pd


def load_weather(root: str | Path, state: str) -> dict[str, float | str]:
	files = sorted(Path(root).glob(f"nasa_power_{state}_*_complete.csv"))
	if not files:
		files = sorted(Path(root).glob(f"nasa_power_{state}_*.csv"))
	if not files:
		return {"date": None, "rainfall_mm": None, "temperature_celsius": None, "humidity_percent": None, "et0_mm": None}
	frame = pd.read_csv(files[0], parse_dates=["date"])
	return {
		"date": None,
		"rainfall_mm": float(frame["PRECTOTCORR"].mean()),
		"temperature_celsius": float(frame["T2M"].mean()),
		"humidity_percent": float(frame["RH2M"].mean()),
		"et0_mm": float("nan"),
	}
