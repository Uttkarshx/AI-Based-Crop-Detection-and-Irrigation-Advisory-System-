import numpy as np

from src.features.feature_pipeline import build_features


def test_feature_pipeline():
	values = np.ones((2, 2), dtype=float)
	features = build_features(
		{"B02": values, "B03": values, "B04": values, "B08": values, "B11": values, "B12": values},
		{"vv": values, "vh": values, "incidence_angle": values},
	)
	assert {"ndvi", "evi", "ndwi", "ndmi", "savi", "vv", "vh", "vh_vv_ratio"} <= features.keys()
