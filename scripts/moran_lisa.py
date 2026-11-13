"""Table 3 (Moran's I, LISA high-high) — Sect. 2.6 / 3.3.
Crude rates per 1,000 per year and empirical Bayes (EB)-smoothed rates for 109 tambons, January 2022 - November 2024
(33 months, December excluded); global Moran's I on log EB-smoothed rates with Queen contiguity weights and
999 permutations (EB Moran's I of Assuncao and Reis as an alternative); LISA high-high clusters under
Benjamini-Hochberg FDR control (alpha = 0.05).
usage: python scripts/moran_lisa.py data/processed results"""
import os, sys, numpy as np, pandas as pd, geopandas as gpd, libpysal, esda, warnings
from esda.smoothing import Empirical_Bayes
warnings.filterwarnings("ignore")
D, OUT = sys.argv[1:3]; os.makedirs(OUT, exist_ok=True)
START, END, N_MONTHS, PERM, SEED, ALPHA = "2022-01", "2024-11", 33, 999, 2026, 0.05
GROUPS = {"Respiratory": ["COPD", "Asthma", "Pneumonia", "Influenza", "Acute pharyngitis", "Chronic rhinitis", "Bronchitis"],
          "Cardiovascular": ["Ischemic heart diseases", "Cerebrovascular diseases (Stroke)"],
          "Eye": ["กลุ่มโรคตาอักเสบ"], "Skin": ["กลุ่มโรคผิวหนังอักเสบ"]}
code6 = lambda s: s.astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(6).str[:6]

H = pd.read_csv(os.path.join(D, "hdc_saraburi_pm25_disease_tambon_monthly_2565_2569.csv"), encoding="utf-8-sig", dtype={"a_code": str})
H["a_code"] = code6(H.a_code); H = H[(H.ym >= START) & (H.ym <= END) & ~H.ym.astype(str).str.endswith("-12")]
assert H.ym.nunique() == N_MONTHS
cnt = H.groupby("a_code")[sum(GROUPS.values(), [])].sum()
T = gpd.read_file(os.path.join(D, "sat_pm25_tambon_summary.gpkg")); T["a_code"] = code6(T.a_code)
T = T.drop_duplicates("a_code"); T = T[T.a_code.isin(cnt.index)].sort_values("a_code").reset_index(drop=True)
py = T["pop"].values * N_MONTHS / 12                                   # person-years (WorldPop 2020)
w = libpysal.weights.Queen.from_dataframe(T, use_index=False, silence_warnings=True); w.transform = "r"
print(f"{len(T)} tambons, {N_MONTHS} months; islands: {w.islands}")

rows, tamb = [], T[["a_code", "name"]].copy()
for g, cols in GROUPS.items():
    y = cnt.loc[T.a_code, cols].sum(axis=1).values.astype(float)
    eb = Empirical_Bayes(y, py).r.ravel() * 1000
    np.random.seed(SEED); mi = esda.Moran(np.log(eb), w, permutations=PERM)
    np.random.seed(SEED); mr = esda.Moran_Rate(y, py, w, permutations=PERM)
    np.random.seed(SEED); li = esda.Moran_Local(np.log(eb), w, permutations=PERM)
    p = li.p_sim; order = np.argsort(p); m = len(p)
    q = np.empty(m); q[order] = np.minimum.accumulate((p[order] * m / np.arange(1, m + 1))[::-1])[::-1]   # BH q-values
    hh_fdr = int(((li.q == 1) & (q <= ALPHA)).sum()); hh_raw = int(((li.q == 1) & (p <= ALPHA)).sum())
    rows.append(dict(outcome=g, visits=int(y.sum()), crude_median=np.median(y / py * 1000),
                     moran_I=mi.I, moran_p=mi.p_sim, eb_moran_I=mr.I, eb_moran_p=mr.p_sim,
                     lisa_HH_fdr=hh_fdr, lisa_HH_unadjusted=hh_raw))
    tamb[f"{g}_eb_rate"] = eb; tamb[f"{g}_lisa_q"] = li.q; tamb[f"{g}_lisa_p"] = p; tamb[f"{g}_lisa_fdr_q"] = q
R = pd.DataFrame(rows)
R.to_csv(os.path.join(OUT, "Table3_moran_lisa.csv"), index=False, encoding="utf-8-sig")
tamb.to_csv(os.path.join(OUT, "Table3_lisa_tambon.csv"), index=False, encoding="utf-8-sig")
pd.set_option("display.width", 160)
print(R.assign(**{"Moran's I (p)": R.apply(lambda r: f"{r.moran_I:.3f} ({r.moran_p:.2f})", axis=1)})
       [["outcome", "Moran's I (p)", "eb_moran_I", "eb_moran_p", "lisa_HH_fdr", "lisa_HH_unadjusted"]].round(3).to_string(index=False))
