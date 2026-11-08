# Satellite-derived PM2.5 and acute illness in Saraburi, Thailand

Code for:

> Sarnjanthuk S, Mahavik N, Umponstira C, Klomjek P. *Satellite-derived PM2.5 and acute illness in Saraburi, Thailand: a Bayesian spatio-temporal study.* Air Quality, Atmosphere & Health (submitted).

The analysis links monthly satellite-derived PM2.5 with acute-illness service visits in 109 sub-districts (tambons) of Saraburi Province, January 2022 – November 2024, using negative binomial models with a BYM2 spatial random effect (PyMC + NumPyro).

Archived version: DOI `10.5281/zenodo.XXXXXXX` <!-- TODO: add after the Zenodo release -->

---

## Repository layout

```
.
├── README.md
├── LICENSE                 MIT (code)
├── requirements.txt
├── notebooks/              Google Colab notebooks, numbered in run order
├── scripts/                HDC download script
└── data/
    ├── raw/                not redistributed — see "Data sources"
    └── processed/          tambon-level tables needed to rerun the models (CC BY 4.0)
```

## Run order and outputs

Run the notebooks in this order. Each one reads the outputs of the steps before it. Every notebook runs in Google Colab (Runtime ▸ Run all); a CPU runtime is enough except where noted.

| Step | File | Produces | Manuscript |
|---:|---|---|---|
| 0 | `scripts/Paper3_00_HDC_download_monthly.py` | Tambon × month visit counts for 11 PM2.5-related conditions | Sect. 2.2 |
| 1 | `notebooks/Paper3_13_DataPrep_Tambon.ipynb` | Tambon × month analysis table; visit summaries | Table 2 |
| 2 | `notebooks/Paper3_06_SatPM25_Tambon_Validation.ipynb` | Population-weighted tambon PM2.5; validation against 41 PCD stations | Sect. 3.1, Fig. 2, Fig. 3, Fig. 4a |
| 3 | `notebooks/Paper3_08_Roadside_Population_H1_H2.ipynb` | Share of tambon population within 150/300/500 m of Highways 1 and 2 | Sect. 2.4, Fig. 4c, sensitivity (vi) |
| 4 | `notebooks/Paper3_21_Proposal_Alignment.ipynb` <!-- TODO: confirm this notebook produces the downwind indicator; otherwise name the one that does --> | Downwind indicator (within 5 km of a DIW facility at 270–315°) | Sect. 2.4, Fig. 4b |
| 5 | `notebooks/Paper3_14_MoranI_Illness_Tambon.ipynb` | Global Moran's I on log EB-smoothed rates | Table 3 |
| 6 | `notebooks/Paper3_15_LISA.ipynb` | Local Moran's I with Benjamini–Hochberg FDR | Table 3 |
| 7 | `notebooks/Paper3_16_SpaceTime_Scan.ipynb` | Space–time permutation scan clusters | Table 3, Fig. 5 |
| 8 | `notebooks/Paper3_18_RateRatio.ipynb` | Exposure-zone rate ratios (Poisson, calendar-year strata, clustered CIs) | Sect. 3.4 |
| 9 | `notebooks/Paper3_20_NB_BYM2_Main.ipynb` (GPU recommended) | NB-BYM2 and NB-iid models; within/between-tambon IRRs; effect modification; predicted risk; sensitivity analyses (i)–(vii) | Sect. 3.5–3.8, Fig. 6, Fig. 7, Fig. 8, Table 6, Table S2 |
| 10 | `notebooks/Paper3_23_Table4_5_FiscalYear.ipynb` (GPU recommended) | Model comparison and out-of-sample prediction; IRR table | Table 4, Table 5 |
| 11 | `notebooks/Paper3_24_SensVII_KaengKhoi_TanDiao.ipynb` | Sensitivity (vii) with Kaeng Khoi and Tan Diao combined | Sect. 2.11 (vii), Sect. 3.7, Table S2 |
| 12 | `notebooks/Paper3_01_Fig1_StudyArea.ipynb` | Study-area map | Fig. 1 |

Table 1 (outcome definitions) is taken from the HDC report specification and is not computed.

### Model settings (Sect. 2.8)

NB-BYM2 in PyMC 5.28 with the NumPyro NUTS sampler: 4 chains × 300 tuning + 300 draws, target acceptance 0.9 (raised to 0.97 where needed). Convergence: R-hat ≤ 1.01, bulk and tail ESS > 400, no divergent transitions. Exposure lags 0, 1 and the 0–1 mean. Sensitivity analyses use negative binomial models with tambon fixed effects (statsmodels).

## Data sources

| Data | Source | Used in | Redistributed here |
|---|---|---|---|
| Acute-illness visits, PM2.5-related disease report, monthly, Jan 2022 – Sep 2026 | Health Data Center, Ministry of Public Health, Thailand (MOPH Open Data) | Steps 0–1 | Tambon × month aggregate counts in `data/processed/` |
| Satellite PM2.5, SatPM2.5 V6.GL.03, monthly, 0.01° | Atmospheric Composition Analysis Group, Washington University in St. Louis | Step 2 | No — download from the ACAG website |
| Ground PM2.5, daily, 41 stations within 200 km (incl. 24T, 25T) | Pollution Control Department, Air4Thai | Steps 2, 9 | No |
| Population, 2020, 100 m | WorldPop | Steps 2–3 | No |
| Temperature, relative humidity, rainfall, hourly | ERA5, Copernicus Climate Change Service (ECMWF) | Step 9 | No |
| Registered factories | Department of Industrial Works, Thailand | Steps 4, 12 | No |
| Highway 1 and 2 centrelines | OpenStreetMap contributors (Geofabrik extract), ODbL | Steps 3, 12 | Yes (`data/processed/osm_highway_1_2.geojson`) |
| Tambon boundaries | <!-- TODO: DOPA / GADM 4.1 / OpenGISData-Thailand — must match Sect. 2.1 --> | All spatial steps | Yes (`data/processed/Saraburi_tambon_boundaries.geojson`) |
| District and province boundaries | OCHA COD-AB via `prasertcbs/thailand_gis` | Step 12 | No — downloaded by the notebook |

### Files in `data/processed/`

<!-- TODO: list after export; at minimum: -->
- `analysis_panel_total_lag0_satscale.csv` — tambon × month panel used by steps 9 and 11
- `Saraburi_tambon_boundaries.geojson` — 111 tambon polygons
- `osm_highway_1_2.geojson` — Highway 1 and 2 centrelines

## Reproducing the analysis

1. Open a notebook in Google Colab.
2. The notebooks were written to read inputs from Google Drive by file ID. To run them from this repository, upload `data/processed/` to your own Drive and replace the IDs in the first code cell of each notebook with your file paths, or set `DATA_DIR` to a local folder.
3. Run the steps in the order above.

Software: Python 3, pandas, geopandas, libpysal, esda, statsmodels, PyMC 5.28, NumPyro, ArviZ 0.22, matplotlib. Exact versions are in `requirements.txt`.

## Notes

- Visits are assigned to the tambon of the reporting facility, not the patient's residence. Kaeng Khoi Hospital (facility 10807) was coded to Kaeng Khoi tambon until December 2024 and to Tan Diao from January 2025 (Sect. 2.2).
- Two tambons, Na Chong and Nong Saeng, had no reporting facility and are excluded (Online Resource 1, Table S1).

## Licence and citation

Code: MIT. Processed data: CC BY 4.0, subject to the terms of the original data providers.

Please cite the article and the archived version (DOI above).

## Contact

Songwut Sarnjanthuk, Faculty of Agriculture, Natural Resources and Environment, Naresuan University — songwuts65@nu.ac.th
