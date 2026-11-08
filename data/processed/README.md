# data/processed

Tambon-level inputs read by the notebooks when they are opened from this repository (each notebook's first code cell sets `DATA_DIR` to this folder; the original Google Drive paths remain as a fallback). Licence: CC BY 4.0, subject to the terms of the original data providers.

| File | Contents | Source | Read by |
|---|---|---|---|
| `hdc_saraburi_pm25_disease_tambon_monthly_2565_2569.csv` | Visits for 11 PM2.5-related conditions, tambon × month, Jan 2022 – Sep 2026 | HDC, Ministry of Public Health (aggregate counts) | 20, 21, 23 |
| `hdc_saraburi_pm25_disease_tambon_annual_2565_2570.csv` | Same, tambon × fiscal year, with population | HDC, Ministry of Public Health | 13, 15, 16, 18 |
| `analysis_panel_total_lag0_satscale.csv` | Tambon × month analysis panel (5,533 rows, 109 tambons, 51 months with satellite PM2.5, Jan 2022 – Sep 2026) written by notebook 20 | derived | 24 |
| `sat_pm25_tambon_monthly.csv` | Population-weighted satellite PM2.5, tambon × month | ACAG SatPM2.5 V6.GL.03 + WorldPop 2020 | 06, 20 |
| `sat_pm25_tambon_summary.gpkg` | Tambon polygons with period-mean satellite PM2.5 | as above | 06, 20, 21, 23 |
| `pm25_tambon_monthly_fy2565_2569.csv` | Tambon × month PM2.5 used in the models | as above | 06, 20, 21, 23 |
| `saraburi_tambon_boundary.gpkg` | 111 tambon polygons (`tambon_id`, `a_code`, `name`) | OCHA COD-AB Thailand (RTSD), via HDX | 06, 08, 13, 15, 16, 18 |
| `Saraburi_tambon_boundaries.geojson` | Same 111 tambons, GeoJSON | OCHA COD-AB Thailand (RTSD) | 01 |
| `saraburi_tambon_rates.gpkg` | 92 tambons with crude and EB-smoothed rates (training version) | derived | 14 |
| `roadside_tambon.csv` | Share of tambon population within 150/300/500 m of Highways 1 and 2 | WorldPop 2020 + OSM | 08, 23 |
| `osm_highway_1_2.geojson` | Highway 1 and 2 centrelines | © OpenStreetMap contributors (ODbL) | 01, 20, 21, 23 |
| `diw_facilities_geocoded.csv` | 295 geocoded DIW-registered facilities used for the downwind indicator | Department of Industrial Works | 21, 23 |
| `saraburi_factories_with_coords.csv` | 391 DIW factory records with coordinates (Fig. 1 shows the 384 within the province) | Department of Industrial Works | 01 |
| `ERA5_cache/era5_14.50_101.00_<year>_<hash>.csv.gz` | Hourly temperature, relative humidity, precipitation, wind, 2022–2024, at 14.50° N 101.00° E | ERA5 via the Open-Meteo archive API | 23 (other years are downloaded when needed) |
