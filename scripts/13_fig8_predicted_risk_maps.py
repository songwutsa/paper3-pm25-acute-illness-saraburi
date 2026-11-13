"""Fig. 8 — predicted respiratory visit ratio, exceedance probability and surveillance-priority tambons (NB-BYM2 + PM2.5).
usage: python scripts/13_fig8_predicted_risk_maps.py results/11_main_nb_bym2/Risk_all_tambons.csv data/processed/sat_pm25_tambon_summary.gpkg figures/Figure_8"""
import sys, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
src, gpkg, out = sys.argv[1:4]
R = pd.read_csv(src, encoding="utf-8-sig", dtype={"a_code": str})
T = gpd.read_file(gpkg).to_crs("EPSG:32647"); T["a_code"] = T.a_code.astype(str).str.zfill(6).str[:6]
T = T.drop_duplicates("a_code")
G = T.merge(R, on="a_code", how="left"); NOFAC = G.SIR.isna()
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
fig, axs = plt.subplots(1, 3, figsize=(16, 6), constrained_layout=True)
v = 8.3
a = axs[0]; G[NOFAC].plot(ax=a, color="#d9d9d9", edgecolor="white", lw=.3)
G[~NOFAC].assign(l2=np.log2(G.SIR)).plot("l2", ax=a, cmap="RdBu_r", vmin=-v, vmax=v, edgecolor="white", lw=.3,
                                          legend=True, legend_kwds={"label": "log$_2$ predicted visit ratio (SIR)", "shrink": .7})
a.set_title("(a) Predicted visit ratio", loc="left", fontsize=11)
a = axs[1]; G[NOFAC].plot(ax=a, color="#d9d9d9", edgecolor="white", lw=.3)
G[~NOFAC].plot("P_RR_gt1", ax=a, cmap="viridis", vmin=0, vmax=1, edgecolor="white", lw=.3,
               legend=True, legend_kwds={"label": "P(RR > 1 | data)", "shrink": .7})
a.set_title("(b) Exceedance probability", loc="left", fontsize=11)
a = axs[2]
cls = np.where(G.priority.fillna(False).astype(bool), "Surveillance priority",
      np.where(G.risk_class == "elevated", "Elevated (other)", np.where(G.risk_class == "uncertain", "Uncertain", "Low")))
COL = {"Surveillance priority": "#b2182b", "Elevated (other)": "#f4a582", "Uncertain": "#f7f7f7", "Low": "#92c5de"}
G[NOFAC].plot(ax=a, color="#d9d9d9", edgecolor="0.4", lw=.3)
for k, c in COL.items():
    s = G[(~NOFAC) & (cls == k)]
    if len(s): s.plot(ax=a, color=c, edgecolor="0.4", lw=.3)
a.legend(handles=[Patch(facecolor=c, edgecolor="0.4", label=k) for k, c in COL.items()] +
         [Patch(facecolor="#d9d9d9", edgecolor="0.4", label="No reporting facility")], loc="upper left", fontsize=8, frameon=False)
a.set_title("(c) Surveillance-priority tambons", loc="left", fontsize=11)
for a in axs: a.set_axis_off()
for ext in ("png", "pdf"): fig.savefig(f"{out}.{ext}", dpi=300, bbox_inches="tight")
print(pd.Series(cls[~NOFAC]).value_counts().to_dict())
