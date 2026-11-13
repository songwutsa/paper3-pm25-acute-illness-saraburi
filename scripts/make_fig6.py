"""Fig. 6 — within-tambon IRR (95% CrI) per 10 µg/m3 by outcome group and lag (NB-BYM2; Table 5).
usage: python scripts/make_fig6.py results/nb23/Table5_IRR_long.csv figures/Figure_6"""
import sys, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
src, out = sys.argv[1:3]
T = pd.read_csv(src, encoding="utf-8-sig")
GROUPS = ["Respiratory", "Cardiovascular", "Eye", "Skin"]
LAGS = [("Lag 0", "#2c7bb6"), ("Lag 1", "#d7191c"), ("Lag 0–1", "#1a9641")]
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10})
fig, ax = plt.subplots(figsize=(6.6, 4.4))
for gi, g in enumerate(GROUPS):
    for li, (lag, col) in enumerate(LAGS):
        r = T[(T.outcome == g) & (T.term == lag)].iloc[0]; y = -gi - li * 0.22
        ax.errorbar(r.IRR, y, xerr=[[r.IRR - r.lo], [r.hi - r.IRR]], fmt="o", ms=6, capsize=3, color=col,
                    label=lag if gi == 0 else None)
ax.axvline(1, ls="--", c="k", lw=1.2)
ax.set_yticks([-gi - 0.22 for gi in range(len(GROUPS))], GROUPS)
ax.set_xlabel("Within-tambon IRR per 10 µg/m³ PM$_{2.5}$ (95% CrI)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=3, frameon=False, fontsize=9)
plt.tight_layout()
for ext in ("png", "pdf"): fig.savefig(f"{out}.{ext}", dpi=300, bbox_inches="tight")
