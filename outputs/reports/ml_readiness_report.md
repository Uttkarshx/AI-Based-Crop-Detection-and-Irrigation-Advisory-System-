# ML Readiness Report

## Overall Status

NOT READY for direct model training.

The processed files are usable as field-level feature tables for further data preparation, but they are not yet reliable supervised-learning datasets for the planned tasks. The main blockers are missing crop-name mapping, missing stress and growth-stage targets, missing temporal observations, non-genuine processed dates, incomplete seven-state coverage, and missing water-balance inputs.

## Processed Datasets

- `data/processed/train.csv`: 400 field-level records, 47 columns.
- `data/processed/validation.csv`: 100 field-level records, 47 columns.
- `data/processed/test.csv`: 412 field-level records, 47 columns and no labels.
- Combined records: 912 unique `field_id` values.
- The files contain one aggregated row per field, not one row per raster pixel.
- No processed raster or pixel-level feature files are present.
- Numeric feature columns are stored as `float64`; identifiers and state/split fields are strings.
- No `Inf` values and no duplicate complete records were found.
- Train, validation, and test field IDs do not overlap.
- Current state coverage is only Bihar, Odisha, Rajasthan, and Uttar Pradesh. Punjab, Haryana, and Jharkhand have no rows in the processed files.

## Crop Classification

Status: NOT READY

Reason:

- Sentinel-2 features, Sentinel-1 features, coordinates, state, and field IDs are present for the training rows.
- `crop_class_id` is present for all 500 labeled rows, but `crop_label` is null for all 500 rows.
- The observed training label codes are `1, 2, 3, 4, 5, 6, 8, 9, 13, 14, 15, 16, 36`.
- The configured crop model declares only `wheat`, `rice`, and `maize`.
- No official numeric-code-to-crop-name mapping is present in the repository, so the configured target cannot be verified.
- The AgriFieldNet test set contains field-ID rasters only and has no crop labels, which is expected for an external test set.
- Optical-only and SAR-only feature subsets can be formed, but supervised training must wait for an approved label mapping and class-scope decision.

## Stress Detection

Status: NOT READY

Reason:

- `stress_label` is null for all 912 processed rows.
- Generic `soil_moisture_percent`, `soil_temperature_celsius`, and `et0_mm` are null for all rows.
- Weather features exist, and soil source values exist for the four represented states, but they are not sufficient to create a validated stress target.
- No stress-label source or stress-label mapping is present.

## Growth Stage Detection

Status: NOT READY

Reason:

- `growth_stage_label` is null for all 912 rows.
- Every current processed row has the same date value, `2025-12-31`.
- The current raw Sentinel-2 filenames do not provide a trustworthy observation date.
- The processed date was therefore not demonstrated to be a satellite acquisition date.
- There are no genuine multi-temporal observations, phenology sequences, or growth-stage labels.
- Growth-stage modelling cannot start from the current processed files.

## Water Deficit Modelling

Status: NOT READY

Reason:

- `et0_mm`, soil moisture, and soil temperature are null for every row.
- NASA POWER provides rainfall, temperature, humidity, wind, and solar radiation, but the processed table uses aggregate weather values and does not align them to a verified satellite observation date.
- No validated crop coefficient/Kc time series, root-zone water balance, irrigation history, or water-deficit target is present.
- Water-deficit modelling cannot start directly from these files.

## Spatial Alignment

PASS for the current field-level aggregation, with limitations.

- Sentinel-2 and train ground-truth rasters have identical CRS, transform, resolution, dimensions, and bounds for all 500 checked training fields.
- Sentinel-1 uses different UTM CRSs and grids for many fields, including EPSG:32645 while Sentinel-2/ground truth also use EPSG:32643 and EPSG:32644 in other fields. The pipeline reprojects and resamples Sentinel-1 before feature aggregation.
- Ground-truth categorical rasters use nearest-neighbor semantics in the alignment utility.
- SoilGrids uses a different CRS and resolution and is sampled after coordinate transformation.
- The final files are field-level means/summary features, so they do not preserve per-pixel alignment evidence. Pixel-level crop mapping or pixel-level segmentation is not supported by the current outputs.
- The raw Sentinel-2 and ground-truth grids are spatially compatible for the fields represented in the training data.

## Temporal Alignment

LIMITED

- NASA POWER complete files cover 2020-01-01 through 2025-12-31 with 2,192 daily rows, no duplicate dates, and no missing dates for all seven state files.
- The final processed files contain one unique date, `2025-12-31`, for every row.
- That date is not verified as the Sentinel-1 or Sentinel-2 acquisition date and should not be used as a temporal observation date.
- Current data is effectively single-snapshot field data. It is not sufficient for growth-stage modelling, temporal stress modelling, or temporal crop modelling.

## Label Quality

FAIL for supervised training readiness.

- Train crop label rasters exist for 500 fields and background value `0` is excluded when deriving the dominant field label.
- Train field-ID rasters exist and field identity is preserved.
- Test field-ID rasters exist for 707 fields; test crop-label rasters are not present.
- Raw labels contain 13 distinct positive numeric codes, while the project configuration declares three crop classes.
- The official code mapping and intended class filtering are missing from the repository.
- No evidence of pixel corruption was found, and Sentinel-2/ground-truth grids match for all checked training fields.

## Missing Data

- `crop_label`: 912 missing values.
- `growth_stage_label`: 912 missing values.
- `stress_label`: 912 missing values.
- `soil_moisture_percent`: 912 missing values.
- `soil_temperature_celsius`: 912 missing values.
- `et0_mm`: 912 missing values.
- Sentinel-1 summary features are missing for all 412 test rows because the collected Sentinel-1 files are train-only.
- The raw SoilGrids collection contains state/property indexing gaps; processed rows exist only for four states.
- No infinite values were found.

## Data Leakage Risk

MEDIUM

- Current train, validation, and test files have no overlapping field IDs.
- Splitting is field-level rather than pixel-level, which avoids the most direct field leakage.
- The final CSV `split` column is inconsistent: validation rows retain the source value `train`, so consumers must use filenames or regenerate splits rather than trusting that column.
- No spatial holdout or geography-based generalization split is present.
- The current field-level aggregate representation prevents pixel leakage but cannot support pixel-level spatial leakage analysis.

## Train/Validation/Test Readiness

PARTIALLY READY

- The mechanical split is usable for field-level experiments: 400 train, 100 validation, and 412 external test fields.
- The test set is unlabeled and contains no Sentinel-1 features.
- The crop target is not training-ready until numeric labels are mapped and reconciled with the configured classes.
- Validation rows should have corrected split metadata before training code consumes the table.

## Blocking Issues

- Approve and add the official AgriFieldNet numeric crop-code mapping.
- Resolve the mismatch between 13 observed label codes and the three configured crop classes.
- Regenerate processed outputs without assigning `2025-12-31` as a fabricated satellite date; use a verified acquisition date or an explicit missing date.
- Add or explicitly exclude Punjab, Haryana, and Jharkhand from the current modelling scope because they have no processed field rows.
- Do not start stress or growth-stage training until their labels and required observations exist.
- Do not start water-deficit modelling until ET0, soil-moisture/water-balance inputs, temporal weather joins, and targets are available.

## Non-Blocking Limitations

- Current outputs are field-level summaries rather than pixel-level datasets.
- Test rows do not contain labels by design and do not contain Sentinel-1 summaries.
- Soil source layers include multiple depths, but the current processed table uses only selected 0-5 cm properties.
- Weather values are present but are aggregate state-level summaries rather than date-matched observations.
- The current split metadata should be corrected before downstream consumers rely on it.

## Final Recommendation

Can we move directly to Model Training now? **No.**

First complete the official crop-code mapping and class-scope decision, regenerate the processed crop dataset with verified temporal metadata, and correct split metadata. After those checks, the first candidate is a field-level crop-classification experiment using the approved crop labels. Stress detection, growth-stage detection, and water-deficit modelling must wait for their missing labels and temporal/water-balance inputs.
