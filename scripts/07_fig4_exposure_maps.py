"""Fig. 4 and Sect. 2.4 / 3.1 — tambon exposure variables.
(a) population-weighted mean PM2.5, 2016-2024; (b) tambons downwind of DIW facilities
(interior point within 5 km of a facility at a bearing of 247.5-337.5 deg from it; same rule as notebooks/11);
(c) share of population within 500 m of Highway 1 or 2. Tambons without a reporting facility are hatched.
usage: python scripts/07_fig4_exposure_maps.py data/processed figures/Figure_4"""
import os, sys, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from pyproj import Geod
D, out = sys.argv[1:3]
NO_FACILITY = ["190106", "190501"]                                   # Na Chong, Nong Saeng
DOWNWIND_SECTOR, DOWNWIND_KM = (247.5, 337.5), 5.0
PM_COL, ROAD_COL = "pm25_pop_all", "share_500m_MAIN"
code6 = lambda s: s.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6).str[:6]
T = gpd.read_file(os.path.join(D, "sat_pm25_tambon_summary.gpkg")); T["a_code"] = code6(T.a_code); T = T.drop_duplicates("a_code")
RS = pd.read_csv(os.path.join(D, "roadside_tambon.csv"), encoding="utf-8-sig", dtype={"a_code": str}); RS["a_code"] = code6(RS.a_code)
T = T.merge(RS[["a_code", ROAD_COL]], on="a_code", how="left"); T[ROAD_COL] = T[ROAD_COL].fillna(0)
DIW = pd.read_csv(os.path.join(D, "diw_facilities_geocoded.csv")).dropna(subset=["lat", "lon"])

UTM, GEOD = "EPSG:32647", Geod(ellps="WGS84")
pt = T.to_crs(UTM).representative_point().to_crs(4326); lat, lon = pt.y.values, pt.x.values
lo_, hi_ = DOWNWIND_SECTOR; dw = np.zeros(len(T), bool)
for la, lo in zip(DIW.lat, DIW.lon):
    az, _, d = GEOD.inv(np.full(len(T), lo), np.full(len(T), la), lon, lat)
    dw |= (d / 1000 <= DOWNWIND_KM) & (az % 360 >= lo_) & (az % 360 <= hi_)
T["downwind"] = dw.astype(int); T["no_facility"] = T.a_code.isin(NO_FACILITY); an = ~T.no_facility
print(f"facilities {len(DIW)}; downwind: {dw.sum()} of {len(T)} tambons; {int(T.loc[an, 'downwind'].sum())} of {int(an.sum())} analysed")
print(f"PM2.5 2016-2024: median {T[PM_COL].median():.1f} (range {T[PM_COL].min():.1f}-{T[PM_COL].max():.1f}) ug/m3")
nz = T.loc[an & (T[ROAD_COL] > 0), ROAD_COL]
print(f"analysed tambons with population within 500 m: {len(nz)} (median share {nz.median():.0%})")

P = T.to_crs(UTM)
fig, axs = plt.subplots(1, 3, figsize=(15, 5.6), constrained_layout=True)
def frame(ax, title):
    ax.set_title(title, loc="left", fontsize=11); ax.set_axis_off()
    P.loc[P.no_facility].plot(ax=ax, facecolor="none", edgecolor="0.3", hatch="///", linewidth=0.5)
P.plot(column=PM_COL, cmap="YlOrRd", ax=axs[0], edgecolor="white", linewidth=0.3, legend=True,
       legend_kwds={"label": "PM$_{2.5}$ (µg/m³)", "shrink": 0.6})
frame(axs[0], "(a) Population-weighted PM$_{2.5}$, 2016–2024")
P.plot(ax=axs[1], color=np.where(P.downwind == 1, "#d95f02", "#e8e8e8"), edgecolor="white", linewidth=0.3)
F = gpd.GeoDataFrame(DIW, geometry=gpd.points_from_xy(DIW.lon, DIW.lat), crs=4326).to_crs(UTM)
F = F[F.within(P.union_all().buffer(2000))]
F.plot(ax=axs[1], markersize=6, color="black", marker="^", linewidth=0)
frame(axs[1], f"(b) Downwind of a facility ({lo_:g}–{hi_:g}°, ≤ {DOWNWIND_KM:g} km)")
axs[1].legend(handles=[Patch(color="#d95f02", label=f"Downwind ({int(P.downwind.sum())})"),
                       Patch(color="#e8e8e8", label=f"Not downwind ({int((P.downwind == 0).sum())})"),
                       Line2D([], [], marker="^", color="black", lw=0, markersize=6, label="DIW facility"),
                       Patch(facecolor="none", edgecolor="0.3", hatch="///", label="No reporting facility")],
              loc="upper left", bbox_to_anchor=(0, 0.02), ncol=2, fontsize=8, frameon=False)
zero = P[ROAD_COL] == 0
P.loc[zero].plot(ax=axs[2], color="#f0f0f0", edgecolor="white", linewidth=0.3)
P.loc[~zero].plot(column=ROAD_COL, cmap="Blues", ax=axs[2], edgecolor="white", linewidth=0.3, legend=True, vmin=0,
                  legend_kwds={"label": "Share of population within 500 m", "shrink": 0.6, "format": lambda x, _: f"{x:.0%}"})
frame(axs[2], "(c) Population within 500 m of Highway 1 or 2")
axs[2].legend(handles=[Patch(color="#f0f0f0", label="No population within 500 m"),
                       Patch(facecolor="none", edgecolor="0.3", hatch="///", label="No reporting facility")],
              loc="upper left", bbox_to_anchor=(0, 0.02), ncol=2, fontsize=8, frameon=False)
for ext in ("png", "pdf"): fig.savefig(f"{out}.{ext}", dpi=300)
