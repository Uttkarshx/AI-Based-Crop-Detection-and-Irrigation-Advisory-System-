# Crop Classification Dataset Readiness

## Dataset Summary

The crop-classification dataset was rebuilt from the available AgriFieldNet, Sentinel-1, Sentinel-2, SoilGrids, and NASA POWER inputs. Each row is one field-level observation with aggregated raster features. The raw Sentinel-2 and ground-truth grids align exactly per field; the final table is not a pixel-level dataset.

Final path: `data/processed/crop_classification/`

Files:

- `train.csv`
- `validation.csv`
- `test.csv`
- `feature_groups.json`

## Number of Samples

- Train: 400 labeled samples
- Validation: 100 labeled samples
- Test: 412 unlabeled samples
- Total: 912 unique field-level samples

## Number of Fields

912 unique `field_id` values. No duplicate field IDs occur across the final files.

## States Present

Available in the final dataset:

- Bihar
- Odisha
- Rajasthan
- Uttar Pradesh

Not present because compatible raw Sentinel/ground-truth observations were not available in the current collection:

- Punjab
- Haryana
- Jharkhand

No samples were fabricated for missing states.

## Crop Classes Present

The official 13-class mapping is configuration-driven in `configs/crops/default.yaml`:

- 1: wheat
- 2: mustard
- 3: lentil
- 4: fallow
- 5: green_pea
- 6: sugarcane
- 8: garlic
- 9: maize
- 13: gram
- 14: coriander
- 15: potato
- 16: bersem
- 36: rice

Present in the available labeled data: wheat, mustard, lentil, fallow, green_pea, sugarcane, garlic, maize, gram, potato, rice.

No available labeled samples were found for coriander (14) or bersem (16). They remain valid configured classes but cannot be trained until samples are available.

## Class Distribution

| Code | Label | Training fields |
|---:|---|---:|
| 1 | wheat | 168 |
| 2 | mustard | 90 |
| 3 | lentil | 2 |
| 4 | fallow | 81 |
| 5 | green_pea | 1 |
| 6 | sugarcane | 14 |
| 8 | garlic | 2 |
| 9 | maize | 25 |
| 13 | gram | 2 |
| 14 | coriander | 0 |
| 15 | potato | 3 |
| 16 | bersem | 0 |
| 36 | rice | 12 |

The class distribution is severely imbalanced. No automatic resampling was applied.

## Feature Groups

### Sentinel-2

Available optical bands and indices include coastal, blue, green, red, red-edge bands, NIR, water-vapor, SWIR bands, NDVI, EVI, NDWI, NDMI, and SAVI. The optical-only feature group is recorded in `feature_groups.json`.

### Sentinel-1

Training rows include VV, VH, VH/VV ratio, and incidence angle summaries. Test rows have missing SAR summaries because the available Sentinel-1 collection is train-only. The SAR-only and optical-plus-SAR feature groups are defined in `feature_groups.json`.

### Soil

The final table includes spatially sampled 0-5 cm clay, pH, sand, silt, and SOC values. SoilGrids source files contain additional depth layers and bulk-density source data, but those are not currently included in the master table.

### Weather

The final table includes state-level aggregate rainfall, temperature, and humidity context from NASA POWER. The complete NASA POWER files cover 2020-01-01 through 2025-12-31 with no duplicate or missing daily dates. Weather values are not pixel-level observations.

## Label Validation

PASS for labeled train and validation rows.

- `crop_code` is sourced from AgriFieldNet label rasters.
- `crop_label` is generated only through the configured official mapping.
- Background value 0 is excluded from dominant field-label extraction.
- Train and validation rows have non-null valid labels.
- Test rows correctly remain unlabeled.
- No unsupported crop codes were found in the processed training rows.

## Spatial Alignment

PASS for the current field-level representation.

- Sentinel-2 and ground-truth rasters match in CRS, transform, resolution, dimensions, and bounds for all 500 train fields.
- Sentinel-1 is reprojected/resampled to the Sentinel-2/ground-truth reference grid before aggregation.
- SoilGrids is sampled after coordinate transformation.
- Categorical ground-truth alignment uses nearest-neighbor semantics.

The final CSV preserves field-level association, not per-pixel alignment metadata.

## Temporal Metadata

LIMITED.

The exact Sentinel-1/Sentinel-2 acquisition date is not available in the current source filenames or raster metadata. The rebuilt crop dataset leaves `date` explicitly null rather than using the previous fabricated `2025-12-31` value. NASA POWER dates are valid independently, but the aggregate weather values are not joined to a verified satellite acquisition date.

This is acceptable as non-fabricated metadata for a snapshot crop experiment, but not for temporal modelling.

## Train/Validation/Test Split

PASS for field-level leakage control.

- Train: 400 fields
- Validation: 100 fields
- Test: 412 fields
- Every output row has split metadata matching its file.
- Train/validation/test field-ID intersections are empty.
- The split is field-level, not random pixel-level.

## Leakage Check

PASS for field-ID leakage. No field appears in more than one split, and no duplicate field IDs occur in the final dataset.

Spatial holdout by geographic region is not implemented; this remains a generalization limitation rather than direct field leakage.

## Missing Data

Expected missing values:

- `crop_code` and `crop_label` in unlabeled test rows
- Sentinel-1 fields in test rows
- `date` for all rows because exact satellite acquisition date is unavailable
- growth-stage, stress, soil-moisture, soil-temperature, and ET0 fields, which are outside this task

Train and validation crop targets contain no missing values. No infinite feature values were found.

## Removed Samples

The final build produced 912 rows from the compatible train/test field associations. Rows without compatible Sentinel-2/ground-truth associations or outside configured study-area bounds were skipped. No raw data was modified.

The current processed coverage remains limited to four states.

## Final ML Readiness

NOT READY for the complete project acceptance criteria.

The available four-state, 11-class labeled subset is technically suitable for a field-level crop-classification experiment using:

- optical-only features
- SAR-only features on labeled training data
- optical-plus-SAR features on labeled training data

However, the complete project dataset is not ready to mark READY because:

1. Punjab, Haryana, and Jharkhand have no compatible processed observations.
2. Coriander and bersem have no available training samples.
3. Exact satellite acquisition dates are unavailable.
4. The dataset is field-level aggregated data, not pixel-level observations.
5. The class distribution is severely imbalanced.
6. Test rows do not have Sentinel-1 summaries.

The first model-training phase can begin only if the scope is explicitly approved as an available-data, four-state, 11-class field-level experiment. It must not be described as the complete seven-state 13-class project dataset.
