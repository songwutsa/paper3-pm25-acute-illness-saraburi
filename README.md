# Satellite-derived PM2.5 and acute illness in Saraburi, Thailand

Code and processed data for:

> Sarnjanthuk S, Mahavik N, Umponstira C, Klomjek P. *Satellite-derived PM2.5 and acute illness in Saraburi, Thailand: a Bayesian spatio-temporal study.* Air Quality, Atmosphere & Health (submitted).

The analysis links monthly satellite-derived PM2.5 with acute-illness service visits in 109 sub-districts (tambons) of Saraburi Province, January 2022 – November 2024, using negative binomial models with a BYM2 spatial random effect (PyMC + NumPyro).

Archived version: DOI `10.5281/zenodo.XXXXXXX` <!-- TODO: add after the Zenodo release -->

---

## Quick start

Click **Open in Colab** next to any notebook below, then **Runtime ▸ Run all**. The first code cell clones this repository into the Colab session and reads the inputs from `data/processed/`, so no Google Drive access is needed. Outputs (tables, figures) are written to the Colab working folder.

To run locally instead: `git clone https://github.com/songwutsa/paper3-pm25-acute-illness-saraburi`, `pip install -r requirements.txt`, and start Jupyter in the repository. Set `USE_REPO = False` in the first cell to use the original Google Drive paths.

## Repository layout

```
.
├── README.md
├── LICENSE                 MIT (code)
├── requirements.txt
├── notebooks/              Google Colab notebooks
├── scripts/                HDC download script
└── data/
    ├── raw/                not redistributed — see "Data sources"
    └── processed/          tambon-level inputs read by the notebooks (CC BY 4.0) — see data/processed/README.md
```

## Run order and outputs

| Step | Notebook | Produces | Manuscript | Runs from repo data | Open |
|---:|---|---|---|:---:|---|
| 0 | `scripts/Paper3_00_HDC_download_monthly.py` | Tambon × month visit counts for 11 PM2.5-related conditions | Sect. 2.2 | — | — |
| 1 | `Paper3_13_DataPrep_Tambon.ipynb` | Tambon × month analysis table; visit summaries | Table 2 | raw downloads† | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_13_DataPrep_Tambon.ipynb) |
| 2 | `Paper3_06_SatPM25_Tambon_Validation.ipynb` | Population-weighted tambon PM2.5; validation against 41 PCD stations | Sect. 3.1, Fig. 2, Fig. 3, Fig. 4a | raw downloads† | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_06_SatPM25_Tambon_Validation.ipynb) |
| 3 | `Paper3_08_Roadside_Population_H1_H2.ipynb` | Share of tambon population within 150/300/500 m of Highways 1 and 2 | Sect. 2.4, Fig. 4c, sensitivity (vi) | raw downloads† | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_08_Roadside_Population_H1_H2.ipynb) |
| 4 | `Paper3_23_Table4_5_FiscalYear.ipynb` (GPU recommended) | Downwind indicator (within 5 km of a DIW facility at 270–315°); model comparison and out-of-sample prediction; IRR table | Sect. 2.4, Fig. 4b, Table 4, Table 5 | ✓ | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_23_Table4_5_FiscalYear.ipynb) |
| 5 | `Paper3_14_MoranI_Illness_Tambon.ipynb` | Global Moran's I on log EB-smoothed rates | Table 3 | ✓ | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_14_MoranI_Illness_Tambon.ipynb) |
| 6 | `Paper3_15_LISA.ipynb` | Local Moran's I with Benjamini–Hochberg FDR | Table 3 | ✓‡ | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_15_LISA.ipynb) |
| 7 | `Paper3_16_SpaceTime_Scan.ipynb` | Space–time permutation scan clusters | Table 3, Fig. 5 | ✓‡ | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_16_SpaceTime_Scan.ipynb) |
| 8 | `Paper3_18_RateRatio.ipynb` | Exposure-zone rate ratios (Poisson, calendar-year strata, clustered CIs) | Sect. 3.4 | ✓‡ | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_18_RateRatio.ipynb) |
| 9 | `Paper3_20_NB_BYM2_Main.ipynb` (GPU recommended) | NB-BYM2 and NB-iid models; within/between-tambon IRRs; effect modification; predicted risk; sensitivity analyses (i)–(vii) | Sect. 3.5–3.8, Fig. 6, Fig. 7, Fig. 8, Table 6, Table S2 | ✓ | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_20_NB_BYM2_Main.ipynb) |
| 10 | `Paper3_21_Proposal_Alignment.ipynb` | Supplementary checks against the study proposal (downwind sector 247.5–337.5°) | — | ✓ | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_21_Proposal_Alignment.ipynb) |
| 11 | `Paper3_24_SensVII_KaengKhoi_TanDiao.ipynb` | Sensitivity (vii) with Kaeng Khoi and Tan Diao combined | Sect. 2.11 (vii), Sect. 3.7, Table S2 | ✓ | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_24_SensVII_KaengKhoi_TanDiao.ipynb) |
| 12 | `Paper3_01_Fig1_StudyArea.ipynb` | Study-area map | Fig. 1 | ✓ | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/songwutsa/paper3-pm25-acute-illness-saraburi/blob/main/notebooks/Paper3_01_Fig1_StudyArea.ipynb) |

† Steps 1–3 build the processed tables from raw inputs that are not redistributed (satellite PM2.5 rasters, WorldPop, PCD station data). Their first cells use the tambon boundaries in `data/processed/`; the raw files must be downloaded from the sources below. Their outputs are already in `data/processed/`, so steps 4–12 do not depend on running them.

‡ Notebooks 15, 16 and 18 can add NASA FIRMS fire counts. Set `FIRMS_MAP_KEY` to your own free key (https://firms.modaps.eosdis.nasa.gov/api/map_key) or leave it empty to skip that part.

Table 1 (outcome definitions) is taken from the HDC report specification and is not computed.

### Model settings (Sect. 2.8)

NB-BYM2 in PyMC 5.28 with the NumPyro NUTS sampler: 4 chains × 300 tuning + 300 draws, target acceptance 0.9 (raised to 0.97 where needed). Convergence: R-hat ≤ 1.01, bulk and tail ESS > 400, no divergent transitions. Exposure lags 0, 1 and the 0–1 mean. Sensitivity analyses use negative binomial models with tambon fixed effects (statsmodels).

## Data sources

| Data | Source | Used in | In this repository |
|---|---|---|---|
| Acute-illness visits, PM2.5-related disease report, monthly, Jan 2022 – Sep 2026 | Health Data Center, Ministry of Public Health, Thailand (MOPH Open Data) | Steps 0–1, 4–11 | Aggregate tambon counts (`hdc_saraburi_pm25_disease_tambon_*.csv`) |
| Satellite PM2.5, SatPM2.5 V6.GL.03, monthly, 0.01° | Atmospheric Composition Analysis Group, Washington University in St. Louis | Step 2 | Tambon averages only — rasters from the ACAG website |
| Ground PM2.5, daily, 41 stations within 200 km (incl. 24T, 25T) | Pollution Control Department, Air4Thai | Step 2 | No |
| Population, 2020, 100 m | WorldPop | Steps 2–3 | Tambon summaries only |
| Temperature, relative humidity, rainfall, hourly | ERA5 (Copernicus Climate Change Service), via the Open-Meteo archive API | Steps 4, 9 | 2022–2024 cache (`ERA5_cache/`) |
| Registered factories | Department of Industrial Works, Thailand | Steps 4, 9, 12 | Yes (`diw_facilities_geocoded.csv`, `saraburi_factories_with_coords.csv`) |
| Highway 1 and 2 centrelines | OpenStreetMap contributors (Geofabrik extract), ODbL | Steps 3, 4, 9, 12 | Yes (`osm_highway_1_2.geojson`) |
| Tambon boundaries | OCHA Common Operational Datasets – Administrative Boundaries (COD-AB) for Thailand, from the Royal Thai Survey Department, via the Humanitarian Data Exchange | All spatial steps | Yes (`saraburi_tambon_boundary.gpkg`, `Saraburi_tambon_boundaries.geojson`) |
| District and province boundaries | OCHA COD-AB via `prasertcbs/thailand_gis` | Step 12 | No — downloaded by the notebook |

The full file list is in [`data/processed/README.md`](data/processed/README.md).

Software: Python 3, pandas, geopandas, libpysal, esda, statsmodels, PyMC, NumPyro, ArviZ, matplotlib. Versions used for the paper are in `requirements.txt`.

## Notes

- Visits are assigned to the tambon of the reporting facility, not the patient's residence. Kaeng Khoi Hospital (facility 10807) was coded to Kaeng Khoi tambon until December 2024 and to Tan Diao from January 2025 (Sect. 2.2).
- Two tambons, Na Chong and Nong Saeng, had no reporting facility and are excluded (Online Resource 1, Table S1).
- Notebook 14 is the training version of the Moran's I analysis (92 tambons, GADM boundaries).

## Licence and citation

Code: MIT. Processed data: CC BY 4.0, subject to the terms of the original data providers.

Please cite the article and the archived version (DOI above).

## Contact

Songwut Sarnjanthuk, Faculty of Agriculture, Natural Resources and Environment, Naresuan University — songwuts65@nu.ac.th
