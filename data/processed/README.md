# data/processed

Tambon-level inputs read by the notebooks and scripts when they are run from this repository (each notebook's first code cell points the data folder here; the original Google Drive paths remain as a fallback). Licence: CC BY 4.0, subject to the terms of the original data providers.

| File | Contents | Source | Written by → read by (step) |
|---|---|---|---|
| `hdc_saraburi_pm25_disease_tambon_monthly_2565_2569.csv` | Visits for 11 PM2.5-related conditions, tambon × month, Jan 2022 – Sep 2026 | HDC, Ministry of Public Health (aggregate counts) | 00 → 08, 09, 11, 14, 15 |
| `sat_pm25_tambon_monthly.csv` | Population-weighted satellite PM2.5, tambon × month | ACAG SatPM2.5 V6.GL.03 + WorldPop 2020 | 01 → 06 |
| `sat_pm25_tambon_summary.gpkg` | Tambon polygons with period-mean satellite PM2.5 and WorldPop population | as above | 01 → 07, 08, 09, 10, 11, 13, 14, 15 |
| `pm25_tambon_monthly_fy2565_2569.csv` | Tambon × month PM2.5 used in the models (satellite to Dec 2024; station-based estimates for 2025–2026) | as above | 01 → 11, 14, 15, 17 |
| `sat_validation_monthly_pairs.csv` | 2,939 station-months at 41 PCD stations within 200 km, 2016–2024: monthly station mean (`obs`), satellite value of the containing cell (`sat`) and 3×3 mean (`sat_3x3`), season | Air4Thai (PCD) + SatPM2.5 V6.GL.03 | 01 → 02, 05 |
| `saraburi_tambon_boundary.gpkg` | 111 tambon polygons (`tambon_id`, `a_code`, `name`) | OCHA COD-AB Thailand (RTSD), via HDX | input of 01, 03 |
| `roadside_tambon.csv` | Share of tambon population within 150/300/500 m of Highways 1 and 2 | WorldPop 2020 + OSM | 03 → 07, 11, 14 |
| `Saraburi_tambon_boundaries.geojson` | Same 111 tambons, GeoJSON | OCHA COD-AB Thailand (RTSD) | input of 04 |
| `osm_highway_1_2.geojson` | Highway 1 and 2 centrelines | © OpenStreetMap contributors (ODbL) | input of 04 |
| `saraburi_factories_with_coords.csv` | 391 DIW factory records with coordinates (Fig. 1 shows the 384 within the province) | Department of Industrial Works | input of 04 |
| `diw_facilities_geocoded.csv` | 295 geocoded DIW-registered facilities used for the downwind indicator (230 cement/quarry/stone, 40 waste/recycling, 25 power) | Department of Industrial Works | input of 07, 11, 14 |
| `ERA5_cache/era5_14.50_101.00_<year>_<hash>.csv.gz` | Hourly temperature, relative humidity, precipitation, wind, 2022–2024, at 14.50° N 101.00° E | ERA5 via the Open-Meteo archive API | input of 11, 14 (other years are downloaded when needed) |
| `analysis_panel_total_lag0_satscale.csv` | Extended tambon × month panel for sensitivity (vii): 5,533 rows, 109 tambons, 51 months, Jan 2022 – Sep 2026 (December, Nov 2025 and Jul 2026 excluded); satellite PM2.5 to Dec 2024, station-estimated with the satellite-scale ratio from Jan 2025 | derived | 15 → 16, 17 |
