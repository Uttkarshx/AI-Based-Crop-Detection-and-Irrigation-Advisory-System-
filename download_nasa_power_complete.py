import requests
import pandas as pd
from pathlib import Path
import time

locations = {
    "punjab": (30.90, 75.85),
    "haryana": (29.06, 76.09),
    "uttar_pradesh": (26.85, 80.95),
    "bihar": (25.59, 85.14),
    "rajasthan": (26.91, 75.79),
    "odisha": (20.30, 85.80),
    "jharkhand": (23.61, 85.28),
}

parameters = [
    "PRECTOTCORR",
    "T2M",
    "RH2M",
    "WS2M",
    "ALLSKY_SFC_SW_DWN",
]

start_date = "20200101"
end_date = "20251231"

output_dir = Path("data/raw/meteorological/nasa_power")
output_dir.mkdir(parents=True, exist_ok=True)

for state, (lat, lon) in locations.items():

    output_file = output_dir / (
        f"nasa_power_{state}_daily_2020_2025_complete.csv"
    )

    print(f"\nDownloading: {state}")
    print(f"Location: {lat}, {lon}")

    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters={','.join(parameters)}"
        f"&community=AG"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start={start_date}"
        f"&end={end_date}"
        f"&format=JSON"
    )

    try:
        response = requests.get(url, timeout=120)
        response.raise_for_status()

        data = response.json()

        records = data["properties"]["parameter"]

        # Correct orientation:
        # rows = dates
        # columns = meteorological parameters
        df = pd.DataFrame(records)

        df.index.name = "date"
        df.reset_index(inplace=True)

        # NASA POWER dates are YYYYMMDD
        df["date"] = pd.to_datetime(
            df["date"].astype(str),
            format="%Y%m%d"
        )

        df.to_csv(output_file, index=False)

        print(f"Saved: {output_file}")
        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")

    except Exception as e:
        print(f"ERROR downloading {state}: {e}")

    time.sleep(2)

print("\n======================================")
print("NASA POWER DOWNLOAD COMPLETE")
print("======================================")