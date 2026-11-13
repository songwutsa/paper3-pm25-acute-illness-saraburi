"""Extended tambon x month panel for sensitivity (vii): January 2022 - September 2026, December excluded
(51 months; November 2025 and July 2026 have no data), 109 tambons, all 11 conditions.
PM2.5 = population-weighted satellite PM2.5 where available, otherwise the satellite-scaled station estimate
(pm25_eq15_satscale). pm_w = (PM2.5 - tambon mean)/10, pm_b = (tambon mean - overall mean)/10.
Reproduces data/processed/analysis_panel_total_lag0_satscale.csv exactly (input of notebooks/16 and script 17).
usage: python scripts/15_build_extended_panel.py data/processed data/processed/analysis_panel_total_lag0_satscale.csv"""
import sys, os, numpy as np, pandas as pd, geopandas as gpd
D = sys.argv[1]
DIS = ["COPD", "Asthma", "Pneumonia", "Influenza", "Acute pharyngitis", "Chronic rhinitis", "Bronchitis",
       "Ischemic heart diseases", "Cerebrovascular diseases (Stroke)", "กลุ่มโรคตาอักเสบ", "กลุ่มโรคผิวหนังอักเสบ"]
H = pd.read_csv(os.path.join(D, "hdc_saraburi_pm25_disease_tambon_monthly_2565_2569.csv"), encoding="utf-8-sig", dtype={"a_code": str})
H["a_code"] = H.a_code.str.zfill(6)
H = H[(H.ym >= "2022-01") & (H.ym <= "2026-09") & ~H.ym.str.endswith("-12")]
P = pd.read_csv(os.path.join(D, "pm25_tambon_monthly_fy2565_2569.csv"), encoding="utf-8-sig", dtype={"a_code": str}); P["a_code"] = P.a_code.str.zfill(6)
sat = P.pm25_source.eq("satellite")
P["pm"] = np.where(sat, P.pm25_sat_pop, P.pm25_eq15_satscale); P["pm_src"] = np.where(sat, "satellite", "eq15_satscale")
T = gpd.read_file(os.path.join(D, "sat_pm25_tambon_summary.gpkg")); T["a_code"] = T.a_code.astype(str).str.zfill(6).str[:6]
df = H[["a_code", "ym", "fy_be"] + DIS + ["flag_incomplete"]].merge(P[["a_code", "ym", "nearest_station", "pm", "pm_src"]], on=["a_code", "ym"], how="inner")
df = df.dropna(subset=["pm"]).merge(T[["a_code", "name", "pop"]].drop_duplicates("a_code"), on="a_code")
df["pm_use"] = df.pm; df["y"] = df[DIS].sum(axis=1)
df["pm_mean_i"] = df.groupby("a_code").pm_use.transform("mean")
df["pm_b"] = (df.pm_mean_i - df.pm_use.mean()) / 10
df["pm_w"] = (df.pm_use - df.pm_mean_i) / 10; df["pm_c"] = df.pm_w + df.pm_b
df["moy"] = df.ym.str[5:].astype(int); df["fy"] = df.fy_be; df["log_pop"] = np.log(df["pop"])
df = df.sort_values(["a_code", "ym"]).reset_index(drop=True)
df["tidx"] = df.a_code.map({a: i for i, a in enumerate(sorted(df.a_code.unique()))})
df = df[["a_code", "ym", "nearest_station", "fy_be", "pm", "pm_src", "pm_use"] + DIS + ["flag_incomplete", "name", "pop", "y", "pm_mean_i", "pm_b", "pm_w", "pm_c", "moy", "fy", "log_pop", "tidx"]]
print(df.shape, df.a_code.nunique(), df.ym.nunique())
df.to_csv(sys.argv[2], index=False, encoding="utf-8-sig")
