"""Sect. 2.3/3.1 — agreement of satellite PM2.5 with station PM2.5 on deseasonalised monthly anomalies.
usage: python scripts/02_validation_anomaly_r2.py data/processed/sat_validation_monthly_pairs.csv   (output of notebooks/01)"""
import sys, numpy as np, pandas as pd, statsmodels.formula.api as smf
d = pd.read_csv(sys.argv[1], parse_dates=["time"]); d["moy"] = d.time.dt.month; d["yr"] = d.time.dt.year
r2 = lambda a, b: np.corrcoef(a, b)[0, 1] ** 2
for c in ["obs", "sat"]: d[c + "_a"] = d[c] - d.groupby(["sid", "moy"])[c].transform("mean")   # station × calendar-month climatology
k = d.groupby(["sid", "moy"]).obs.transform("size") > 1
print(f"pooled R2 {r2(d.obs, d.sat):.3f} (n = {len(d)})")
print(f"anomaly R2 {r2(d.obs_a[k], d.sat_a[k]):.3f}, RMSE {np.sqrt(((d.obs_a[k] - d.sat_a[k]) ** 2).mean()):.2f} µg/m3 (n = {k.sum()})")
ro = smf.ols("obs ~ C(sid) + C(moy) + C(yr)", d).fit().resid; rs = smf.ols("sat ~ C(sid) + C(moy) + C(yr)", d).fit().resid
print(f"R2 after station + month-of-year + year adjustment {r2(ro, rs):.3f}")
for s in ["24t", "25t"]:
    x = d[(d.sid.str.lower() == s) & k]; print(f"{s.upper()} anomaly R2 {r2(x.obs_a, x.sat_a):.3f} (n = {len(x)})")
