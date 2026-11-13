"""Fig. 5 — space-time permutation scan clusters by outcome group (output of 09_table3_spacetime_scan.py).
usage: python scripts/10_fig5_scan_cluster_maps.py results/08-09_table3_spatial_clustering/Fig5_scan_clusters.csv data/processed/sat_pm25_tambon_summary.gpkg figures/Figure_5"""
import sys, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
src, gpkg, out = sys.argv[1:4]
R = pd.read_csv(src, encoding="utf-8-sig", dtype={"centre": str})
T = gpd.read_file(gpkg).to_crs("EPSG:32647"); T["a_code"] = T.a_code.astype(str).str.zfill(6)
NOFAC = T.a_code.isin(["190106", "190501"])
MONTHS = [m for m in pd.period_range("2022-01", "2024-11", freq="M").astype(str) if not m.endswith("-12")]
MI = {m: i for i, m in enumerate(MONTHS)}
PAL = ["#b2182b", "#2166ac", "#1b7837", "#e08214", "#762a83", "#35978f", "#c51b7d", "#8c510a", "#4d4d4d", "#7fbc41"]
GROUPS = ["Respiratory", "Cardiovascular", "Eye", "Skin"]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
fig, axs = plt.subplots(2, 4, figsize=(15, 7.6), gridspec_kw={"height_ratios": [1.5, 1]}, constrained_layout=True)
for j, g in enumerate(GROUPS):
    G = R[R.outcome == g].sort_values("rank"); sig = G[G.p < 0.05]
    a = axs[0, j]; T.plot(ax=a, color="#ececec", edgecolor="#bdbdbd", lw=.3)
    T[NOFAC].plot(ax=a, facecolor="none", edgecolor="0.4", hatch="///", lw=.4)
    for _, r in sig.iterrows():
        mem = T[T.a_code.isin(r.tambons.split(";"))]
        mem.plot(ax=a, color=PAL[r["rank"] - 1], alpha=.9 if r["rank"] == 1 else .7, edgecolor="white", lw=.3)
        p = mem.union_all().representative_point()
        a.text(p.x, p.y, str(r["rank"]), ha="center", va="center", fontsize=7.5, fontweight="bold", color="white",
               bbox=dict(boxstyle="circle,pad=0.15", fc="black", ec="none", alpha=.75))
    a.set_axis_off(); a.set_title(f"({'abcd'[j]}) {g}", loc="left", fontsize=10)
    t = axs[1, j]
    for _, r in sig.iterrows():
        y = r["rank"]; s, e = MI[r.start], MI[r.end]
        t.barh(y, e - s + 1, left=s - .5, height=.62, color=PAL[y - 1])
        lab = f"{r.n_tambons} tambon{'s' if r.n_tambons > 1 else ''}, RR {r.RR:.2f}"
        t.text(e + .8 if e < 25 else s - .8, y, lab, va="center", ha="left" if e < 25 else "right", fontsize=6.8)
    t.set_ylim(len(G) + .6, .4); t.set_yticks(range(1, len(G) + 1)); t.set_ylabel("Cluster rank")
    yr = [MI[m] for m in MONTHS if m.endswith("-01")]
    t.set_xticks(yr, [m[:4] for m in MONTHS if m.endswith("-01")]); t.set_xlim(-.5, len(MONTHS) - .5)
    for x in yr[1:]: t.axvline(x - .5, color="0.8", lw=.6, zorder=0)
    t.spines[["top", "right"]].set_visible(False); t.set_xlabel("Month (December excluded)")
fig.legend(handles=[Patch(facecolor="none", edgecolor="0.4", hatch="///", label="No reporting facility (not analysed)")],
           loc="upper right", fontsize=8, frameon=False)
for ext in ("png", "pdf"): fig.savefig(f"{out}.{ext}", dpi=300)
print("non-significant clusters:", R[R.p >= 0.05][["outcome", "rank", "p"]].to_dict("records"))
