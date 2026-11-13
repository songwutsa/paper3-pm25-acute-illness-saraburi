# Satellite-derived PM2.5 and healthcare visits for PM2.5-related conditions in Saraburi, Thailand

Code, processed data and results for:

> Sarnjanthuk S, Mahavik N, Umponstira C, Klomjek P. *Satellite-derived PM2.5 and healthcare visits for PM2.5-related conditions in Saraburi, Thailand: a Bayesian spatio-temporal study.* Air Quality, Atmosphere & Health (submitted).

The analysis links monthly satellite-derived PM2.5 with service visits for 11 PM2.5-related conditions recorded by the Health Data Center (HDC) in 109 sub-districts (tambons) of Saraburi Province, January 2022 – November 2024 (December excluded), using negative binomial models with a BYM2 spatial random effect (PyMC + NumPyro) and negative binomial models with tambon fixed effects for sensitivity analyses.

Archived version: DOI `10.5281/zenodo.XXXXXXX` <!-- TODO: add after the Zenodo release -->

---

## Quick start

- **Notebooks:** click **Open in Colab** in the table below, then **Runtime ▸ Run all**. The first code cell clones this repository and reads the inputs from `data/processed/`; outputs go to the matching `results/` folder of the clone. No Google Drive access is needed.
- **Scripts:** `git clone https://github.com/songwutsa/paper3-pm25-healthcare-visits-saraburi`, `pip install -r requirements.txt`, and run the commands below from the repository root.

## Repository layout

Notebooks and scripts share one numbering, `00`–`17`, which is the order in which they are run. A step only reads files from `data/processed/` or from the `results/` folder of an earlier step.

```
.
├── README.md
├── LICENSE                          MIT (code)
├── requirements.txt
├── notebooks/                       Google Colab notebooks (steps 01, 03, 04, 11, 14, 16)
├── scripts/                         Python scripts (all other steps)
├── data/
│   ├── raw/                         not redistributed — see "Data sources"
│   └── processed/                   tambon-level inputs (CC BY 4.0) — see data/processed/README.md
├── results/
│   ├── 08-09_table3_spatial_clustering/   Table 3 and Fig. 5 data (steps 08, 09)
│   ├── 11_main_nb_bym2/                   Tables 4–6, Sect. 3.4–3.8 (step 11)
│   ├── 14_sensitivity_fixed_effects/      Online Resource 1 Table S2a–c (step 14)
│   └── 16_sensitivity_vii/                Table S2d (step 16)
└── figures/                         Figures 2–6 and 8 as submitted (PNG, 300 dpi)
```

## Run order and what each step produces

| Step | File | Manuscript | Input | Output | Runs from repo data |
|---|---|---|---|---|:---:|
| 00 | `scripts/00_download_hdc_monthly_visits.py` | Sect. 2.2, Table 2 | MOPH Open Data API | `data/processed/hdc_saraburi_pm25_disease_tambon_monthly_2565_2569.csv` | — (online) |
| 01 | `notebooks/01_satellite_pm25_tambon_validation.ipynb` [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-healthcare-visits-saraburi/blob/main/notebooks/01_satellite_pm25_tambon_validation.ipynb) | Sect. 2.3, 3.1 | SatPM2.5 rasters, WorldPop, PCD stations† | `sat_pm25_tambon_monthly.csv`, `sat_pm25_tambon_summary.gpkg`, `pm25_tambon_monthly_fy2565_2569.csv`, `sat_validation_monthly_pairs.csv` | — † |
| 02 | `scripts/02_validation_anomaly_r2.py` | Sect. 3.1 anomaly R² | `sat_validation_monthly_pairs.csv` | printed | ✓ |
| 03 | `notebooks/03_roadside_population_share.ipynb` [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-healthcare-visits-saraburi/blob/main/notebooks/03_roadside_population_share.ipynb) | Sect. 2.4 roadside share | OSM roads, WorldPop† | `roadside_tambon.csv` | — † |
| 04 | `notebooks/04_fig1_study_area_map.ipynb` [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-healthcare-visits-saraburi/blob/main/notebooks/04_fig1_study_area_map.ipynb) | Fig. 1 | `data/processed/` + online district boundaries | Figure 1 | ✓ |
| 05 | `scripts/05_fig2_satellite_validation.py` | Fig. 2 | `sat_validation_monthly_pairs.csv` | `figures/Figure_2.png` | ✓ |
| 06 | `scripts/06_fig3_pm25_seasonal_monthly.py` | Fig. 3 | `sat_pm25_tambon_monthly.csv` | `figures/Figure_3.png` | ✓ |
| 07 | `scripts/07_fig4_exposure_maps.py` | Sect. 2.4, 3.1, Fig. 4 (downwind 247.5–337.5°, roadside share) | `data/processed/` | `figures/Figure_4.png` | ✓ |
| 08 | `scripts/08_table3_moran_lisa.py` | Table 3 (Moran's I, LISA) | `data/processed/` | `results/08-09_table3_spatial_clustering/Table3_*.csv` | ✓ |
| 09 | `scripts/09_table3_spacetime_scan.py` | Table 3 (scan), Sect. 3.3 | HDC monthly, tambon polygons | `results/08-09_table3_spatial_clustering/Fig5_scan_clusters.csv` | ✓ (≈3 min) |
| 10 | `scripts/10_fig5_scan_cluster_maps.py` | Fig. 5 | output of step 09 | `figures/Figure_5.png` | ✓ |
| 11 | `notebooks/11_main_nb_bym2_models.ipynb` [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-healthcare-visits-saraburi/blob/main/notebooks/11_main_nb_bym2_models.ipynb) | Sect. 3.4, Tables 4–6, Sect. 3.5–3.8, Fig. 7, attributable visits | `data/processed/` | `results/11_main_nb_bym2/` | ✓ (GPU recommended, several hours) |
| 12 | `scripts/12_fig6_irr_by_lag.py` | Fig. 6 | `results/11_main_nb_bym2/Table5_IRR_long.csv` | `figures/Figure_6.png` | ✓ |
| 13 | `scripts/13_fig8_predicted_risk_maps.py` | Fig. 8 | `results/11_main_nb_bym2/Risk_all_tambons.csv` | `figures/Figure_8.png` | ✓ |
| 14 | `notebooks/14_sensitivity_fixed_effects.ipynb` [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-healthcare-visits-saraburi/blob/main/notebooks/14_sensitivity_fixed_effects.ipynb) | Sensitivity (i)–(vi), (viii), (ix); Online Resource 1 Table S2a–c | `data/processed/`, `results/11_main_nb_bym2/Table5_IRR_long.csv` | `results/14_sensitivity_fixed_effects/` | ✓ (≈5 min) |
| 15 | `scripts/15_build_extended_panel.py` | Sensitivity (vii) data, Jan 2022 – Sep 2026 | `data/processed/` | `data/processed/analysis_panel_total_lag0_satscale.csv` | ✓ |
| 16 | `notebooks/16_sensitivity_vii_merged_tambons.ipynb` [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-healthcare-visits-saraburi/blob/main/notebooks/16_sensitivity_vii_merged_tambons.ipynb) | Sensitivity (vii), Table S2d | output of step 15 | `results/16_sensitivity_vii/` | ✓ |
| 17 | `scripts/17_sensitivity_vii_station_scale.py` | Sensitivity (vii), station-scale ratio | output of step 15 | printed | ✓ |

† Builds processed tables from raw inputs that are not redistributed (satellite PM2.5 rasters, WorldPop, PCD station data, OSM extract). Its outputs are already in `data/processed/`, so later steps do not depend on running it.

Script commands (from the repository root):

```bash
python scripts/02_validation_anomaly_r2.py data/processed/sat_validation_monthly_pairs.csv
python scripts/05_fig2_satellite_validation.py data/processed/sat_validation_monthly_pairs.csv figures/Figure_2
python scripts/06_fig3_pm25_seasonal_monthly.py data/processed/sat_pm25_tambon_monthly.csv figures/Figure_3
python scripts/07_fig4_exposure_maps.py data/processed figures/Figure_4
python scripts/08_table3_moran_lisa.py data/processed results/08-09_table3_spatial_clustering
python scripts/09_table3_spacetime_scan.py data/processed/hdc_saraburi_pm25_disease_tambon_monthly_2565_2569.csv data/processed/sat_pm25_tambon_summary.gpkg results/08-09_table3_spatial_clustering
python scripts/10_fig5_scan_cluster_maps.py results/08-09_table3_spatial_clustering/Fig5_scan_clusters.csv data/processed/sat_pm25_tambon_summary.gpkg figures/Figure_5
python scripts/12_fig6_irr_by_lag.py results/11_main_nb_bym2/Table5_IRR_long.csv figures/Figure_6
python scripts/13_fig8_predicted_risk_maps.py results/11_main_nb_bym2/Risk_all_tambons.csv data/processed/sat_pm25_tambon_summary.gpkg figures/Figure_8
python scripts/15_build_extended_panel.py data/processed data/processed/analysis_panel_total_lag0_satscale.csv
python scripts/17_sensitivity_vii_station_scale.py data/processed
```

Table 1 (outcome definitions) is taken from the HDC report specification and is not computed. The NB-BYM2 posterior draws (`fits/*.nc`, about 35 MB per model) are not stored here; they are recreated by step 11.

### Reproduction check (13 Nov 2026)

Run from this repository on CPU:

- Step 09 reproduced `Fig5_scan_clusters.csv` exactly, including p-values (seed 2026).
- Step 08 reproduced the four Moran's I values in Table 3. Permutation p-values (seed 2026: 0.48, 0.31, 0.42, 0.29) differ from earlier runs by up to 0.02. No LISA high–high cluster survived FDR control.
- Step 14 reproduced every row of Table S2. Step 15 rebuilt `analysis_panel_total_lag0_satscale.csv` identically, and step 16 reproduced Table S2d from it.
- Step 11 sections 1–4b reproduced the tambon-month table (3,597 rows, 354,785 visits), the downwind indicator (60 of 111 tambons; 59 of 109 analysed) and the Sect. 3.4 rate ratios. The MCMC sections were not rerun; `results/11_main_nb_bym2/` holds the outputs of the run used for the manuscript (10 Nov 2026).
- The figure scripts reproduced the numbers quoted in Sect. 3.1: R² 0.73, RMSE 6.2 µg/m³, Spearman ρ 0.37, seasonal means, and anomaly R² 0.33.

### Model settings (Sect. 2.8)

- **NB-BYM2:** fitted in PyMC 5.28 with the NumPyro NUTS sampler. 4 chains × (300 tuning + 300 draws). Target acceptance 0.9, raised to 0.97 where needed.
- **Convergence criteria:** R-hat ≤ 1.01, bulk and tail ESS > 400, no divergent transitions. Achieved: minimum bulk ESS 855, minimum tail ESS 809.
- **Exposure lags:** 0, 1 and the 0–1 mean.
- **Downwind indicator:** tambon interior point within 5 km of a Department of Industrial Works facility, at a bearing of 247.5–337.5° from the facility.
- **Sensitivity analyses:** NB2 models with tambon fixed effects (statsmodels). Dispersion by profile maximum likelihood.

## Data sources

| Data | Source | In this repository |
|---|---|---|
| Visits for 11 PM2.5-related conditions, monthly, Jan 2022 – Sep 2026 | Health Data Center, Ministry of Public Health, Thailand (MOPH Open Data, report `s_pm25_month`) | Aggregate tambon counts (`hdc_saraburi_pm25_disease_tambon_*.csv`) |
| Satellite PM2.5, SatPM2.5 V6.GL.03, monthly, 0.01° | Atmospheric Composition Analysis Group, Washington University in St. Louis | Tambon averages only — rasters from the ACAG website |
| Ground PM2.5, 41 stations within 200 km (incl. 24T, 25T) | Pollution Control Department, Air4Thai | Monthly station means paired with satellite values (`sat_validation_monthly_pairs.csv`) |
| Population, 2020, 100 m | WorldPop | Tambon summaries only |
| Temperature, relative humidity, rainfall, hourly | ERA5 (Copernicus Climate Change Service), via the Open-Meteo archive API | 2022–2024 cache (`ERA5_cache/`) |
| Registered factories | Department of Industrial Works, Thailand | `diw_facilities_geocoded.csv` (295 used), `saraburi_factories_with_coords.csv` |
| Highway 1 and 2 centrelines | OpenStreetMap contributors (Geofabrik extract), ODbL | `osm_highway_1_2.geojson` |
| Tambon boundaries | OCHA COD-AB Thailand (Royal Thai Survey Department), via the Humanitarian Data Exchange | `saraburi_tambon_boundary.gpkg`, `Saraburi_tambon_boundaries.geojson` |
| District and province boundaries | OCHA COD-AB via `prasertcbs/thailand_gis` | No — downloaded by step 04 |

The full file list is in [`data/processed/README.md`](data/processed/README.md).

## Notes

- Visits are assigned to the tambon of the reporting facility, not to the patient's residence. Kaeng Khoi Hospital (facility 10807) was coded to Kaeng Khoi tambon until December 2024 and to Tan Diao from January 2025 (Sect. 2.2).
- Two tambons, Na Chong and Nong Saeng, had no reporting facility and are excluded (Online Resource 1, Table S1).
- Earlier working notebooks (training versions, the superseded main model and proposal checks) were removed from the repository because no reported number depends on them. Notebook comments that mention *Drive notebook NN* refer to those originals.
- AI assistance (Claude, Anthropic) in writing and checking code is disclosed in Sect. 2.12 of the article.

## Licence and citation

Code: MIT. Processed data and results: CC BY 4.0, subject to the terms of the original data providers.

Please cite the article and the archived version (DOI above).

## Contact

Songwut Sarnjanthuk, Faculty of Agriculture, Natural Resources and Environment, Naresuan University — songwuts65@nu.ac.th
