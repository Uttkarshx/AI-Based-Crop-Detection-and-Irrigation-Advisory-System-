from datetime import date

import pandas as pd


def aggregate_weather(frame: pd.DataFrame) -> dict[str, float | str]:
	if frame.empty:
		return {}
	frame = frame.copy()
	frame["date"] = pd.to_datetime(frame["date"])
	return {
		"date": frame["date"].max().date().isoformat(),
		"rainfall_mm": float(frame["PRECTOTCORR"].mean()),
		"temperature_celsius": float(frame["T2M"].mean()),
		"humidity_percent": float(frame["RH2M"].mean()),
		"et0_mm": float("nan"),
	}
