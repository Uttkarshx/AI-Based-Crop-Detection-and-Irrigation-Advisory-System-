from pathlib import Path

import pandas as pd


def load_weather(root: str | Path, state: str) -> dict[str, float | str]:
	files = sorted(Path(root).glob(f"nasa_power_{state}_*_complete.csv"))
	if not files:
		files = sorted(Path(root).glob(f"nasa_power_{state}_*.csv"))
	if not files:
		return {"date": None, "rainfall_mm": None, "temperature_celsius": None, "humidity_percent": None, "wind_speed_ms": None, "solar_radiation_mj_m2": None, "et0_mm": None}
	frame = pd.read_csv(files[0], parse_dates=["date"])
	return {
		"date": None,
		"rainfall_mm": float(frame["PRECTOTCORR"].mean()),
		"temperature_celsius": float(frame["T2M"].mean()),
		"humidity_percent": float(frame["RH2M"].mean()),
		"wind_speed_ms": float(frame["WS2M"].mean()),
		"solar_radiation_mj_m2": float(frame["ALLSKY_SFC_SW_DWN"].mean()),
		"et0_mm": float("nan"),
	}
