"""Sensitivity (vii), Sect. 3.7 and Online Resource 1 Table S2d footnote — station-scale versus satellite-scale
PM2.5 for January 2025 - September 2026 (all 11 conditions combined, 109 tambons, 51 months).
Same model as notebooks/16: NB with tambon fixed effects, month-of-year and fiscal-year effects, log population offset.
usage: python scripts/17_sensitivity_vii_station_scale.py data/processed"""
import os, sys, numpy as np, pandas as pd, statsmodels.formula.api as smf, warnings
warnings.filterwarnings("ignore")
D = sys.argv[1]
df = pd.read_csv(os.path.join(D, "analysis_panel_total_lag0_satscale.csv"), encoding="utf-8-sig", dtype={"a_code": str})
pm = pd.read_csv(os.path.join(D, "pm25_tambon_monthly_fy2565_2569.csv"), encoding="utf-8-sig", dtype={"a_code": str})
pm["a_code"] = pm.a_code.str.zfill(6)
df = df.merge(pm[["a_code", "ym", "pm25_eq15"]], on=["a_code", "ym"], how="left")
est = df.pm_src != "satellite"                                         # 2025-2026 months estimated from stations 24T/25T
df["pm_station"] = np.where(est, df.pm25_eq15, df.pm_use)              # station-scale ratio instead of satellite-scale

def fit(d, col):
    d = d.copy(); d["pmw"] = (d[col] - d.groupby("a_code")[col].transform("mean")) / 10
    m = smf.negativebinomial("y ~ pmw + C(a_code) + C(moy) + C(fy)", data=d, offset=d["log_pop"])
    r = m.fit(method="bfgs", maxiter=3000, disp=0)
    if not r.mle_retvals.get("converged", True): r = m.fit(method="newton", maxiter=200, disp=0, start_params=r.params)
    b, se = r.params["pmw"], r.bse["pmw"]
    return np.exp(b), np.exp(b - 1.96 * se), np.exp(b + 1.96 * se)

print(f"{len(df):,} tambon-months, {df.a_code.nunique()} tambons, {df.ym.nunique()} months")
print("satellite-scale (notebooks/16 check, expected 1.003): IRR %.3f (%.3f–%.3f)" % fit(df, "pm_use"))
print("station-scale: IRR %.3f (%.3f–%.3f)" % fit(df, "pm_station"))
