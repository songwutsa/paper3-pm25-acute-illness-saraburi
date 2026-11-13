"""Fig. 3 — seasonal and monthly variation of population-weighted satellite PM2.5, Saraburi (111 tambons).
Input: sat_pm25_tambon_monthly.csv (Notebook 06).
usage: python scripts/make_fig3.py data/processed/sat_pm25_tambon_monthly.csv figures/Figure_3"""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
src, out = sys.argv[1:3]
S = pd.read_csv(src, encoding="utf-8-sig", dtype={"a_code": str}); S["t"] = pd.to_datetime(S.time); S["m"] = S.t.dt.month
COL = "pm25_pop"; SEAS = ["Winter", "Summer", "Rainy"]; SC = {"Winter": "#2c7bb6", "Summer": "#d7191c", "Rainy": "#1a9641"}
STUDY = (S.t >= "2022-01") & (S.t <= "2024-11") & (S.m != 12)        # health-data months (December excluded)

prov = S.groupby("t")[COL].agg(["mean", "min", "max"])
seas_mean = S.groupby("season")[COL].mean()
tamb_seas = S.groupby(["a_code", "season"])[COL].mean().unstack()
st = S[STUDY]; mon = st.groupby("m")[COL].mean(); tm = st.groupby("a_code")[COL].mean()
mon_rng = st.groupby(["m", "a_code"])[COL].mean().groupby("m").agg(["min", "max"])
print("season means 2016-2024:", seas_mean.round(1).to_dict())
print("study period: Feb", round(mon[2], 1), "Jul", round(mon[7], 1), "tambon range", round(tm.min(), 1), "-", round(tm.max(), 1))

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
fig = plt.figure(figsize=(10, 7.6), constrained_layout=True); gs = fig.add_gridspec(2, 2, width_ratios=[1, 1.5])
# (a) monthly series 2016-2024
a = fig.add_subplot(gs[0, :])
a.fill_between(prov.index, prov["min"], prov["max"], color="0.85", lw=0, label="Range across tambons")
a.plot(prov.index, prov["mean"], color="black", lw=1.2, label="Provincial mean")
a.axvspan(pd.Timestamp("2022-01-01"), pd.Timestamp("2024-11-30"), color="#fdd49e", alpha=.35, lw=0, label="Health-data period")
a.set_ylabel("PM$_{2.5}$ (µg/m³)"); a.set_ylim(0, 63); a.set_xlim(prov.index.min(), prov.index.max() + pd.offsets.MonthEnd(0))
a.legend(loc="upper right", ncol=3, fontsize=8, frameon=False)
a.set_title("(a) Monthly population-weighted PM$_{2.5}$, 111 tambons, 2016–2024", loc="left")
# (b) seasons 2016-2024
b = fig.add_subplot(gs[1, 0])
bp = b.boxplot([tamb_seas[s] for s in SEAS], tick_labels=SEAS, widths=.55, patch_artist=True, medianprops=dict(color="black"))
for p_, s in zip(bp["boxes"], SEAS): p_.set_facecolor(SC[s]); p_.set_alpha(.45)
for k, s in enumerate(SEAS, 1): b.text(k, tamb_seas[s].max() + .8, f"{seas_mean[s]:.1f}", ha="center", fontsize=8.5)
b.set_ylabel("Tambon seasonal mean (µg/m³)"); b.set_ylim(0, 41)
b.set_title("(b) Seasonal means, 2016–2024", loc="left")
# (c) calendar months, health-data period
c = fig.add_subplot(gs[1, 1]); mm = [m for m in range(1, 13) if m in mon.index]
c.fill_between(mm, mon_rng.loc[mm, "min"], mon_rng.loc[mm, "max"], color="0.85", lw=0, label="Range across tambons")
c.plot(mm, mon[mm], "-o", color="black", ms=3.5, lw=1.2, label="Provincial mean")
for m_ in (2, 7): c.annotate(f"{mon[m_]:.1f}", (m_, mon[m_]), xytext=(6, 4 if m_ == 2 else -11), textcoords="offset points", fontsize=8.5)
c.set_xticks(range(1, 13), ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]); c.set_xlim(.5, 12.5)
c.text(12, 2, "no health\ndata", ha="center", fontsize=7, color="0.4")
c.set_ylabel("PM$_{2.5}$ (µg/m³)"); c.set_ylim(0, None); c.legend(fontsize=8, frameon=False, loc="upper right")
c.set_title("(c) Calendar-month means, Jan 2022–Nov 2024", loc="left")
for ext in ("png", "pdf"): fig.savefig(f"{out}.{ext}", dpi=300)
