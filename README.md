# Satellite-derived PM2.5 and healthcare visits for PM2.5-related conditions in Saraburi, Thailand

Code, processed data and results for:

> Sarnjanthuk S, Mahavik N, Umponstira C, Klomjek P. *Satellite-derived PM2.5 and healthcare visits for PM2.5-related conditions in Saraburi, Thailand: a Bayesian spatio-temporal study.* Air Quality, Atmosphere & Health (submitted).

The analysis links monthly satellite-derived PM2.5 with service visits for 11 PM2.5-related conditions recorded by the Health Data Center (HDC) in 109 sub-districts (tambons) of Saraburi Province, January 2022 – November 2024 (December excluded), using negative binomial models with a BYM2 spatial random effect (PyMC + NumPyro) and negative binomial models with tambon fixed effects for sensitivity analyses.

Archived version: DOI `10.5281/zenodo.XXXXXXX` <!-- TODO: add after the Zenodo release -->

---

## Quick start

- **Notebooks:** click **Open in Colab** below, then **Runtime ▸ Run all**. The first code cell clones this repository and reads the inputs from `data/processed/`; outputs go to `results/<notebook>/` of the clone. No Google Drive access is needed.
- **Scripts:** `git clone https://github.com/songwutsa/paper3-pm25-acute-illness-saraburi`, `pip install -r requirements.txt`, and run the commands in the table from the repository root.

## Repository layout

```
.
├── README.md
├── LICENSE                     MIT (code)
├── requirements.txt
├── notebooks/                  Google Colab notebooks used for the manuscript
│   └── supplementary/          superseded or training notebooks (not used for reported numbers)
├── scripts/                    Python scripts (HDC download, scan statistic, Table 3, figures, checks)
├── data/
│   ├── raw/                    not redistributed — see "Data sources"
│   └── processed/              tambon-level inputs (CC BY 4.0) — see data/processed/README.md
├── results/                    outputs used in the manuscript, by notebook or script
│   ├── nb23/                   Tables 4–6, Sect. 3.4–3.8 (Notebook 23)
│   ├── nb24/                   sensitivity (vii) (Notebook 24)
│   ├── nb25/                   Online Resource 1 Table S2 (Notebook 25)
│   └── table3/                 Table 3 and Fig. 5 (moran_lisa.py, stscan.py)
└── figures/                    Figures 2–6 and 8 as submitted (PNG, 300 dpi)
```

## What produces each result

| Manuscript | Code | Input | Output | Runs from repo data |
|---|---|---|---|:---:|
| Sect. 2.2, Table 2 (HDC download) | `scripts/Paper3_00_HDC_download_monthly.py` | MOPH Open Data API | `data/processed/hdc_saraburi_pm25_disease_tambon_monthly_2565_2569.csv` | — (online) |
| Sect. 2.3, 3.1, Fig. 2 | `notebooks/Paper3_06_SatPM25_Tambon_Validation.ipynb` → `scripts/make_fig2.py` | SatPM2.5 rasters, PCD stations† | `data/processed/sat_validation_monthly_pairs.csv`, `figures/Figure_2.png` | Fig. 2 ✓ |
| Sect. 3.1 anomaly R² | `scripts/validation_anomaly.py` | `sat_validation_monthly_pairs.csv` | printed | ✓ |
| Sect. 3.1, Fig. 3 | `scripts/make_fig3.py` | `sat_pm25_tambon_monthly.csv` | `figures/Figure_3.png` | ✓ |
| Sect. 2.4, 3.1, Fig. 4 (downwind 247.5–337.5°, roadside share) | `scripts/make_fig4.py` (roadside shares from `notebooks/Paper3_08_Roadside_Population_H1_H2.ipynb`†) | `data/processed/` | `figures/Figure_4.png` | ✓ |
| Fig. 1 | `notebooks/Paper3_01_Fig1_StudyArea.ipynb` | `data/processed/` + online district boundaries | Figure 1 | ✓ |
| Table 3 (Moran's I, LISA) | `scripts/moran_lisa.py` | `data/processed/` | `results/table3/Table3_moran_lisa.csv` | ✓ |
| Table 3 (scan), Sect. 3.3, Fig. 5 | `scripts/stscan.py` → `scripts/make_fig5.py` | HDC monthly, tambon polygons | `results/table3/Fig5_scan_clusters.csv`, `figures/Figure_5.png` | ✓ (≈3 min) |
| Sect. 3.4, Tables 4–6, Sect. 3.5–3.8, Fig. 7, attributable visits | `notebooks/Paper3_23_Table4_6_NB_BYM2_FiscalYear.ipynb` (GPU recommended, several hours) | `data/processed/` | `results/nb23/` | ✓ |
| Fig. 6, Fig. 8 | `scripts/make_fig6.py`, `scripts/make_fig8.py` | `results/nb23/` | `figures/Figure_6.png`, `figures/Figure_8.png` | ✓ |
| Sensitivity (i)–(vi), (viii), (ix); Online Resource 1 Table S2a–c | `notebooks/Paper3_25_Sensitivity_FE_FiscalYear.ipynb` (≈5 min) | `data/processed/`, `results/nb23/Table5_IRR_long.csv` | `results/nb25/` | ✓ |
| Sensitivity (vii), Table S2d | `notebooks/Paper3_24_SensVII_KaengKhoi_TanDiao.ipynb` | `analysis_panel_total_lag0_satscale.csv` | `results/nb24/` | ✓ |
| Sensitivity (vii), station-scale ratio | `scripts/station_scale_vii.py` | `data/processed/` | printed | ✓ |
| Tambon data preparation | `notebooks/Paper3_13_DataPrep_Tambon.ipynb` | raw downloads† | tables in `data/processed/` | — |

† Builds processed tables from raw inputs that are not redistributed (satellite PM2.5 rasters, WorldPop, PCD station data). Its outputs are already in `data/processed/`, so the other steps do not depend on running it.

Table 1 (outcome definitions) is taken from the HDC report specification and is not computed. The NB-BYM2 posterior draws (`fits/*.nc`, about 35 MB per model) are not stored here; they are recreated by Notebook 23.

### Reproduction check (13 Nov 2026)

Run from this repository on CPU:

- `stscan.py` reproduced `Fig5_scan_clusters.csv` exactly, including p-values (seed 2026).
- `moran_lisa.py` reproduced the four Moran's I values in Table 3. Permutation p-values (seed 2026: 0.48, 0.31, 0.42, 0.29) differ from earlier runs by up to 0.02. No LISA high–high cluster survived FDR control.
- Notebook 25 reproduced every row of Table S2. Notebook 24 reproduced Table S2d.
- Notebook 23 sections 1–4b reproduced the tambon-month table (3,597 rows, 354,785 visits), the downwind indicator (60 of 111 tambons; 59 of 109 analysed) and the Sect. 3.4 rate ratios. The MCMC sections were not rerun; `results/nb23/` holds the outputs of the run used for the manuscript (10 Nov 2026).
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
| District and province boundaries | OCHA COD-AB via `prasertcbs/thailand_gis` | No — downloaded by Notebook 01 |

The full file list is in [`data/processed/README.md`](data/processed/README.md).

## Notes

- Visits are assigned to the tambon of the reporting facility, not to the patient's residence. Kaeng Khoi Hospital (facility 10807) was coded to Kaeng Khoi tambon until December 2024 and to Tan Diao from January 2025 (Sect. 2.2).
- Two tambons, Na Chong and Nong Saeng, had no reporting facility and are excluded (Online Resource 1, Table S1).
- `notebooks/supplementary/` holds earlier notebooks that are not used for any reported number:
  - Notebooks 14, 15, 16 and 18 are training versions (annual data, 92 tambons, or NASA FIRMS fire counts).
  - Notebook 20 is the earlier main model, replaced by Notebooks 23 and 25.
  - Notebook 21 holds the checks against the study proposal.
- AI assistance (Claude, Anthropic) in writing and checking code is disclosed in Sect. 2.12 of the article.

## Licence and citation

Code: MIT. Processed data and results: CC BY 4.0, subject to the terms of the original data providers.

Please cite the article and the archived version (DOI above).

## Contact

Songwut Sarnjanthuk, Faculty of Agriculture, Natural Resources and Environment, Naresuan University — songwuts65@nu.ac.th
