# Feature Extraction Report

- Total samples: 912
- Total fields: 912
- States: bihar, odisha, rajasthan, uttar_pradesh
- Feature count: 31
- Split counts: {'test': 412, 'train': 400, 'validation': 100}
- Class distribution by field: {(1.0, 'wheat'): 207, (2.0, 'mustard'): 106, (3.0, 'lentil'): 3, (4.0, 'fallow'): 108, (5.0, 'green_pea'): 1, (6.0, 'sugarcane'): 15, (8.0, 'garlic'): 2, (9.0, 'maize'): 36, (13.0, 'gram'): 3, (15.0, 'potato'): 6, (36.0, 'rice'): 13}
- Missing feature/target values: {'vv': 412, 'vh': 412, 'vh_vv_ratio': 412, 'incidence_angle': 412, 'crop_code': 412, 'crop_label': 412}
- Duplicate rows: 0

## Feature Groups

- Sentinel-2 (17): coastal, blue, green, red, red_edge, red_edge_2, red_edge_3, nir, water_vapor, swir1, swir2, red_edge_4, ndvi, evi, ndwi, ndmi, savi
- Sentinel-1 (4): vv, vh, vh_vv_ratio, incidence_angle
- Soil (5): soil_clay_0-5cm, soil_phh2o_0-5cm, soil_sand_0-5cm, soil_silt_0-5cm, soil_soc_0-5cm
- Weather (5): rainfall_mm, temperature_celsius, humidity_percent, wind_speed_ms, solar_radiation_mj_m2

## Outputs

- Master: data\processed\crop_classification\master_dataset.csv
- Optical-only: data\processed\crop_classification\optical_only.csv
- SAR-only: data\processed\crop_classification\sar_only.csv
- Optical+SAR: data\processed\crop_classification\optical_sar.csv
