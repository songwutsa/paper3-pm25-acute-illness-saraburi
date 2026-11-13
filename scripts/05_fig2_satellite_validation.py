"""Fig. 2 and Sect. 3.1 — validation of monthly satellite PM2.5 against PCD stations (41 stations, 2016-2024).
usage: python scripts/05_fig2_satellite_validation.py data/processed/sat_validation_monthly_pairs.csv figures/Figure_2"""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import stats
src, out = sys.argv[1], sys.argv[2]
V = pd.read_csv(src, encoding="utf-8-sig", parse_dates=["time"])
def m(g):
    S, O = g.sat.values, g.obs.values; r = np.corrcoef(S, O)[0, 1]
    return dict(n=len(g), R2=r * r, bias=(S - O).mean(), NMB=(S - O).sum() / O.sum() * 100, RMSE=np.sqrt(((S - O) ** 2).mean()))
P = m(V); print("pooled", P, "stations", V.sid.nunique())
for s in ["Winter", "Summer", "Rainy"]: print(s, round(m(V[V.season == s])["R2"], 2))
LT = V.groupby("sid").agg(obs=("obs", "mean"), sat=("sat", "mean"), n=("obs", "size")).query("n>=24")
rho, p = stats.spearmanr(LT.obs, LT.sat); print("spatial", len(LT), rho, p)
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
COL = {"Winter": "#2c7bb6", "Summer": "#d7191c", "Rainy": "#1a9641"}; LAB = {"Winter": "Winter", "Summer": "Summer", "Rainy": "Rainy"}
fig, ax = plt.subplots(2, 2, figsize=(10, 8.4), constrained_layout=True)
a = ax[0, 0]; mx = np.ceil(np.nanpercentile(V[["obs", "sat"]].values, 99.8) / 10) * 10
for s in ["Rainy", "Summer", "Winter"]:
    g = V[V.season == s]; a.scatter(g.obs, g.sat, s=7, alpha=.4, color=COL[s], lw=0, label=f"{LAB[s]} (R² = {m(g)['R2']:.2f}, n = {len(g):,})")
a.plot([0, mx], [0, mx], "k--", lw=.8); a.set_xlim(0, mx); a.set_ylim(0, mx); a.set_aspect("equal")
a.set_xlabel("Station monthly mean PM$_{2.5}$ (µg/m³)"); a.set_ylabel("Satellite PM$_{2.5}$ (µg/m³)")
a.set_title(f"(a) {V.sid.nunique()} PCD stations, {P['n']:,} station-months", loc="left")
a.text(.03, .97, f"R² = {P['R2']:.2f}\nRMSE = {P['RMSE']:.1f} µg/m³\nBias = {P['bias']:+.1f} µg/m³ (NMB {P['NMB']:+.0f}%)".replace("-", "−"),
       transform=a.transAxes, va="top", fontsize=8.5)
a.legend(loc="lower right", fontsize=7.5, frameon=False, markerscale=2)
for a, sid, lab in [(ax[0, 1], "24t", "(b) Station 24T (industrial roadside)"), (ax[1, 0], "25t", "(c) Station 25T (urban)")]:
    g = V[V.sid == sid].sort_values("time").set_index("time"); M = m(g)
    full = pd.date_range(g.index.min(), g.index.max(), freq="MS"); g = g.reindex(full)
    a.plot(g.index, g.obs, "-o", ms=2.5, lw=1, color="black", label="Station")
    a.plot(g.index, g.sat, "-", lw=1.3, color="#e08214", label="Satellite (1-km cell)")
    a.set_ylabel("PM$_{2.5}$ (µg/m³)"); a.set_ylim(0, None); a.legend(fontsize=8, frameon=False, loc="upper right")
    a.set_title(f"{lab}\nbias {M['bias']:+.1f} µg/m³ ({M['NMB']:+.0f}%), R² = {M['R2']:.2f}".replace("-", "−"), loc="left")
a = ax[1, 1]; a.scatter(LT.obs, LT.sat, s=22, color="#888", lw=0, label="Other PCD stations")
for sid, c in [("24t", "#c0504d"), ("25t", "#4a7fb5")]:
    a.scatter(LT.loc[sid, "obs"], LT.loc[sid, "sat"], s=70, color=c, zorder=3, label=sid.upper())
lo = np.floor(min(LT.obs.min(), LT.sat.min()) - 2); hi = np.ceil(max(LT.obs.max(), LT.sat.max()) + 2)
a.plot([lo, hi], [lo, hi], "k--", lw=.8); a.set_xlim(lo, hi); a.set_ylim(lo, hi); a.set_aspect("equal")
a.set_xlabel("Station long-term mean (µg/m³)"); a.set_ylabel("Satellite long-term mean (µg/m³)")
a.set_title(f"(d) Spatial ranking of long-term means, {len(LT)} stations\nSpearman ρ = {rho:.2f} (p = {p:.3f})", loc="left")
a.legend(fontsize=8, frameon=False, loc="lower right")
for ext in ("png", "pdf"): fig.savefig(f"{out}.{ext}", dpi=300)
