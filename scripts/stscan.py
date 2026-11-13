"""Space-time permutation scan (Kulldorff et al. 2005) for Paper 3, Sect. 2.6 / 3.3 (Table 3, Fig. 5).
Data and windows as in the manuscript: 109 analysed tambons, Jan 2022 - Nov 2024 without December (33 months),
circular windows on tambon interior points holding up to 25% of cases, temporal windows up to 50% of the months,
999 permutations, ten highest-ranked clusters with no tambon in common.
Cluster relative risk: RR = (O/E) / [(C - O) / (C - E)].
usage: python scripts/stscan.py data/processed/hdc_saraburi_pm25_disease_tambon_monthly_2565_2569.csv \
           data/processed/sat_pm25_tambon_summary.gpkg results [N_PERM]"""
import sys, numpy as np, pandas as pd, geopandas as gpd

HDC, GPKG, OUT = sys.argv[1:4]; NPERM = int(sys.argv[4]) if len(sys.argv) > 4 else 999
START, END = "2022-01", "2024-11"; NO_FACILITY = ["190106", "190501"]
MAX_SPACE, MAX_TIME, N_REPORT, SEED = 0.25, 0.50, 10, 2026
GROUPS = {"Respiratory": ["COPD", "Asthma", "Pneumonia", "Influenza", "Acute pharyngitis", "Chronic rhinitis", "Bronchitis"],
          "Cardiovascular": ["Ischemic heart diseases", "Cerebrovascular diseases (Stroke)"],
          "Eye": ["กลุ่มโรคตาอักเสบ"], "Skin": ["กลุ่มโรคผิวหนังอักเสบ"]}
code6 = lambda s: s.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6).str[:6]

T = gpd.read_file(GPKG); T["a_code"] = code6(T.a_code)
T = T[~T.a_code.isin(NO_FACILITY)].drop_duplicates("a_code").sort_values("a_code").reset_index(drop=True)
H = pd.read_csv(HDC, encoding="utf-8-sig", dtype={"a_code": str}); H["a_code"] = code6(H.a_code); H["ym"] = H.ym.astype(str).str[:7]
H = H[(H.ym >= START) & (H.ym <= END) & ~H.ym.str.endswith("-12") & H.a_code.isin(T.a_code)]
MONTHS = sorted(H.ym.unique()); Z, M = len(T), len(MONTHS)
pt = T.to_crs("EPSG:32647").representative_point(); XY = np.c_[pt.x, pt.y]
ORDER = np.argsort(((XY[:, None] - XY[None]) ** 2).sum(-1), axis=1)          # nearest-neighbour order per centre
LMAX = int(np.floor(MAX_TIME * M))
print(f"{Z} tambons x {M} months ({MONTHS[0]} to {MONTHS[-1]}); temporal windows up to {LMAX} months")

def windows_max(cnt, mu, C, kmax):
    """max GLR over all cylinders + its location. cnt, mu: (Z, M)."""
    best = (-np.inf, None)
    for i in range(Z):
        o = ORDER[i, :kmax[i]]
        cc = np.cumsum(cnt[o], 0); cm = np.cumsum(mu[o], 0)            # (k, M): first k neighbours
        cc = np.concatenate([np.zeros((cc.shape[0], 1)), np.cumsum(cc, 1)], 1)
        cm = np.concatenate([np.zeros((cm.shape[0], 1)), np.cumsum(cm, 1)], 1)
        for L in range(1, LMAX + 1):
            c = cc[:, L:] - cc[:, :-L]; m = cm[:, L:] - cm[:, :-L]
            with np.errstate(divide="ignore", invalid="ignore"):
                g = np.where(c > m, c * np.log(c / m) + (C - c) * np.log((C - c) / (C - m)), 0.0)
            j = np.unravel_index(np.argmax(g), g.shape)
            if g[j] > best[0]: best = (g[j], (i, j[0] + 1, j[1], L))
    return best

def all_windows(cnt, mu, C, kmax):
    rows = []
    for i in range(Z):
        o = ORDER[i, :kmax[i]]
        cc = np.cumsum(cnt[o], 0); cm = np.cumsum(mu[o], 0)
        cc = np.concatenate([np.zeros((cc.shape[0], 1)), np.cumsum(cc, 1)], 1)
        cm = np.concatenate([np.zeros((cm.shape[0], 1)), np.cumsum(cm, 1)], 1)
        for L in range(1, LMAX + 1):
            c = cc[:, L:] - cc[:, :-L]; m = cm[:, L:] - cm[:, :-L]
            with np.errstate(divide="ignore", invalid="ignore"):
                g = np.where(c > m, c * np.log(c / m) + (C - c) * np.log((C - c) / (C - m)), 0.0)
            k, t = np.nonzero(g > 0)
            rows.append(np.c_[np.full(len(k), i), k + 1, t, np.full(len(k), L), g[k, t], c[k, t], m[k, t]])
    return np.concatenate(rows)

rng = np.random.default_rng(SEED); RES = []
for g, cols in GROUPS.items():
    X = H.assign(y=H[cols].apply(pd.to_numeric, errors="coerce").fillna(0).sum(axis=1)).groupby(["a_code", "ym"]).y.sum()
    cnt = X.unstack().reindex(index=T.a_code, columns=MONTHS).fillna(0).round().values
    C = cnt.sum(); mu = np.outer(cnt.sum(1), cnt.sum(0)) / C
    zt = cnt.sum(1)
    kmax = np.array([int(np.searchsorted(np.cumsum(zt[ORDER[i]]), MAX_SPACE * C, side="right")) for i in range(Z)])
    kmax = np.maximum(kmax, 1)
    W = all_windows(cnt, mu, C, kmax); W = W[np.argsort(-W[:, 4])]
    # permutation null: shuffle the month of each case, keeping tambon and month totals
    zid = np.repeat(np.arange(Z), zt.astype(int)); mid = np.repeat(np.tile(np.arange(M), 1), cnt.sum(0).astype(int))
    NULL = np.empty(NPERM)
    for r in range(NPERM):
        perm = np.zeros((Z, M)); np.add.at(perm, (zid, rng.permutation(mid)), 1)
        NULL[r] = windows_max(perm, mu, C, kmax)[0]
        if (r + 1) % 200 == 0: print(f"  {g}: {r + 1}/{NPERM}", flush=True)
    used, rep = set(), []
    for i, k, t, L, llr, c, m in W:
        mem = ORDER[int(i), :int(k)]
        if used & set(mem): continue
        used |= set(mem)
        p = (1 + (NULL >= llr).sum()) / (NPERM + 1)
        rep.append(dict(outcome=g, rank=len(rep) + 1, n_tambons=int(k), centre=T.a_code[int(i)],
                        tambons=";".join(T.a_code[mem]), names=";".join(T["name"][mem].astype(str)),
                        start=MONTHS[int(t)], end=MONTHS[int(t) + int(L) - 1], n_months=int(L),
                        observed=int(c), expected=round(m, 1), RR=round((c / m) / ((C - c) / (C - m)), 2),
                        LLR=round(llr, 1), p=round(p, 3)))
        if len(rep) == N_REPORT: break
    R = pd.DataFrame(rep); RES.append(R); print(R.head(5).drop(columns=["tambons"]).to_string(index=False))
pd.concat(RES).to_csv(f"{OUT}/Fig5_scan_clusters.csv", index=False, encoding="utf-8-sig")
