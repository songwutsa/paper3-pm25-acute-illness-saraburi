# -*- coding: utf-8 -*-
"""
00_download_hdc_monthly_visits.py
ดึงข้อมูลรายงาน HDC "โรคที่เกี่ยวข้องกับ PM2.5" (s_pm25_disease) จังหวัดสระบุรี รายตำบล **รายเดือน**
ปีงบประมาณ 2565 ถึงปีล่าสุด แล้วบันทึกเป็น CSV ที่ notebooks/11 และ 14 อ่านได้ทันที (คอลัมน์ a_code + ym)

ข้อเท็จจริงที่ต้องรู้ก่อน
- ตาราง s_pm25_disease ใน MOPH Open Data ดึงได้ทีละ "ปีงบประมาณ" (ไฟล์เดิมได้ ~147 แถวดิบต่อปี = ไม่มีมิติเดือน)
  สคริปต์จึงมี 3 วิธี และ **ตรวจผลทุกครั้ง**: ผลรวม 12 เดือนต้องเท่ากับยอดรายปีงบ และค่ารายเดือนต้องไม่ซ้ำกันทุกเดือน
  ถ้าไม่ผ่าน จะหยุดและไม่บันทึกไฟล์ (ป้องกันการได้ "ยอดทั้งปีซ้ำ 12 เดือน" โดยไม่รู้ตัว)

วิธีที่ 1  --source opendata (ค่าเริ่มต้น)
    ถ้าข้อมูลดิบมีคอลัมน์เดือน/วันที่ จะรวมตามเดือนให้เลย; ถ้าไม่มี จะลองส่งพารามิเตอร์เดือนให้ API (month / b_month)
    แล้วตรวจว่า API ใช้พารามิเตอร์นั้นจริงหรือไม่

วิธีที่ 2  --source template  (ใช้เมื่อวิธีที่ 1 ไม่ได้ — ดึงจากหน้ารายงาน HDC ที่เลือกเดือนได้)
    1) เปิดหน้ารายงาน https://hdc.moph.go.th/sri/public/standard-report-detail/297c1cb035778f7b49357693e6867e6c
    2) กด F12 → แท็บ Network → เลือกจังหวัดสระบุรี ระดับตำบล ปีงบ และ "เดือน" 1 เดือน แล้วกดแสดงรายงาน
    3) คลิกคำขอที่ตอบข้อมูลตาราง (มักเป็น api-hdc.moph.go.th/...) → ดู URL, Method, Request Headers, Payload
    4) สร้างไฟล์ hdc_request_template.json (ตัวอย่างพิมพ์ได้ด้วย --make-template) แล้วแทนค่าปี/เดือนด้วยตัวแปร
         {fy}        ปีงบ พ.ศ. เช่น 2567          {month}  เดือน 1–12        {mm}  เดือน 2 หลัก 01–12
         {year_be}   ปีปฏิทิน พ.ศ. ของเดือนนั้น    {year_ce} ปีปฏิทิน ค.ศ.     {yyyymm_ce} เช่น 202310  {yyyymm_be} เช่น 256610
    5) python scripts/00_download_hdc_monthly_visits.py --source template --template hdc_request_template.json

วิธีที่ 3  --source files --files-dir โฟลเดอร์
    ดาวน์โหลด Excel/CSV จากหน้ารายงาน HDC ทีละเดือนเอง ตั้งชื่อไฟล์ให้มีปีงบและเดือน เช่น 2567_10.xlsx (ปีงบ_เดือน)
    สคริปต์จะรวมเป็นไฟล์เดียวให้

ข้อควรรู้: เว็บกระทรวงสาธารณสุขมักบล็อก IP ต่างประเทศ (เช่น Google Colab) → รันบนเครื่องที่ใช้อินเทอร์เน็ตในไทย

วิธีใช้
    pip install requests pandas openpyxl
    python scripts/00_download_hdc_monthly_visits.py --probe                 (ดูคอลัมน์ดิบของ Open Data 1 ปี — ทำก่อน)
    python scripts/00_download_hdc_monthly_visits.py                         (วิธีที่ 1, ปีงบ 2565 ถึงปีปัจจุบัน)
    python scripts/00_download_hdc_monthly_visits.py --make-template         (พิมพ์ตัวอย่างไฟล์ template)
    python scripts/00_download_hdc_monthly_visits.py --source template --template hdc_request_template.json
    python scripts/00_download_hdc_monthly_visits.py --source files --files-dir hdc_monthly_downloads
    python scripts/00_download_hdc_monthly_visits.py --annual                (แบบเดิม: รายปีงบ)
"""
import argparse, datetime as dt, glob, json, os, re, sys, time

import pandas as pd
import requests

API = "https://opendata.moph.go.th/api/report_data"
TABLE = "s_pm25_disease"
PROVINCE = "19"                       # สระบุรี
HEADERS = {"User-Agent": "curl/8", "Content-Type": "application/json", "Accept": "application/json"}
PAGE = 10000
# ตรวจแล้ว (26 ต.ค. 2569): พารามิเตอร์ "year" ของ s_pm25_disease / s_pm25_month คือ "ปีปฏิทิน พ.ศ." (ม.ค.–ธ.ค.)
#   ยอดปี 2569 ใน s_pm25_disease = ผลรวม ม.ค.–ก.ย. 2569 ของรายงานรายเดือนพอดี และ m1 = ม.ค.
FY_MONTHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]     # เดือนในปี (ปฏิทิน)
MONTHLY_TABLE = "s_pm25_month"                         # รายงานรายเดือน (5968980caf87d4518aa9f0263a9299c6)

COLMAP = {
    "r1_1": "COPD", "r1_2": "Asthma", "r1_3": "Pneumonia", "r1_4": "Influenza",
    "r1_5": "Acute pharyngitis", "r1_6": "Chronic rhinitis", "r1_7": "Bronchitis",
    "r2_1": "Ischemic heart diseases", "r2_2": "Cerebrovascular diseases (Stroke)",
    "r3": "กลุ่มโรคตาอักเสบ", "r4": "กลุ่มโรคผิวหนังอักเสบ",
    "r5": "UNKNOWN_r5",               # Exposure to air pollution
    "r6": "UNKNOWN_r6",               # Lung cancer
}
DISEASE_COLS = list(COLMAP.values())
ELEVEN = DISEASE_COLS[:11]
MONTH_COL_PAT = r"^(b_?)?month$|^mm$|^mon$|^m$|^bmonth$|^month_?id$"
DATE_COL_PAT = r"^date_?serv$|^vstdate$|^date$"
# ชื่อโรคในรายงานรายเดือนของ HDC (5968980caf87d4518aa9f0263a9299c6) → ชื่อมาตรฐาน
NAME_ALIASES = {
    "chronic obstructive pulmonary disease": "COPD", "copd": "COPD", "asthma": "Asthma", "pneumonia": "Pneumonia",
    "influenza": "Influenza", "acute pharyngitis": "Acute pharyngitis", "chronic rhinitis": "Chronic rhinitis",
    "bronchitis": "Bronchitis", "acute ischemic heart disease": "Ischemic heart diseases",
    "ischemic heart diseases": "Ischemic heart diseases", "cerebrovascular disease (stroke)": "Cerebrovascular diseases (Stroke)",
    "cerebrovascular diseases (stroke)": "Cerebrovascular diseases (Stroke)", "กลุ่มโรคตาอักเสบ": "กลุ่มโรคตาอักเสบ",
    "กลุ่มโรคผิวหนังอักเสบ": "กลุ่มโรคผิวหนังอักเสบ", "exposure to air pollution": "UNKNOWN_r5",
    "long-term effect": "UNKNOWN_r6", "lung cancer": "UNKNOWN_r6",
}
MCOL = r"^m(0?[1-9]|1[0-2])$"                            # คอลัมน์รายเดือน m1…m12 (ม.ค.…ธ.ค. ของ "ปี" ในรายงาน)
NAME_SOURCES = ["https://raw.githubusercontent.com/kongvut/thai-province-data/master/api/latest/sub_district.json"]


# ---------------------------------------------------------------- พื้นฐาน
def current_fiscal_year_be(today=None):
    t = today or dt.date.today()
    return t.year + 543 + (1 if t.month >= 10 else 0)


def fy_month_to_calendar(year_be, month):
    """ปี (ปฏิทิน พ.ศ. ตาม API) + เดือน → (ปีปฏิทิน พ.ศ., ค.ศ.)"""
    return year_be, year_be - 543


def post(body, tries=6, url=API, headers=HEADERS):
    for a in range(tries):
        try:
            r = requests.post(url, headers=headers, data=json.dumps(body), timeout=(15, 180))
        except requests.RequestException as e:
            if a == tries - 1:
                raise
            print(f"   ⚠ เชื่อมต่อไม่ได้ ({type(e).__name__}) — ลองใหม่ใน {2 ** a} s"); time.sleep(2 ** a); continue
        if r.status_code in (200, 201):
            return r.json()
        if r.status_code in (429, 502, 503, 504) and a < tries - 1:
            time.sleep(2 ** a); continue
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
    raise RuntimeError("ดึงข้อมูลไม่สำเร็จ")


def fetch_opendata(year, extra=None, table=None):
    rows, offset = [], 0
    while True:
        body = {"tableName": table or TABLE, "year": str(year), "province": PROVINCE, "type": "json", "limit": PAGE, "offset": offset}
        body.update(extra or {})
        res = post(body)
        data = res.get("data", []) if isinstance(res, dict) else (res if isinstance(res, list) else [])
        total = int(res.get("total", len(data))) if isinstance(res, dict) else len(data)
        rows += data
        if not data or len(rows) >= total:
            break
        offset += PAGE; time.sleep(0.4)
    return pd.DataFrame(rows)


def load_names(path=None):
    if path:
        old = pd.read_csv(path, encoding="utf-8-sig", dtype={"a_code": str})
        return dict(zip(old["a_code"].str[:6], old["a_name"]))
    for u in NAME_SOURCES:
        try:
            js = requests.get(u, timeout=60).json(); names = {}
            for t in js:
                code = str(t.get("id") or t.get("code") or "")
                nm = t.get("name_th") or t.get("nameTh") or t.get("name")
                if isinstance(nm, dict): nm = nm.get("th") or nm.get("en")
                if code[:2] == PROVINCE and nm: names[code[:6]] = nm
            if names: return names
        except Exception as e:
            print(f"   ⚠ ชื่อตำบล: {str(e)[:80]}")
    return {}


# ---------------------------------------------------------------- รวมเป็นตำบล
def _area_col(df):
    cols = {c.lower(): c for c in df.columns}
    for k in ("areacode", "area_code", "tambon_code", "tmb_code", "subdistrict_code", "a_code", "code", "id"):
        if k in cols: return cols[k]
    for c in df.columns:                                   # หาเองจากค่า (รหัส 6/8 หลักขึ้นต้น 19)
        s = df[c].astype(str).str.replace(r"\.0$", "", regex=True)
        if s.str.fullmatch(r"19\d{4}(\d{2})?").mean() > 0.8: return c
    raise RuntimeError(f"ไม่พบคอลัมน์รหัสพื้นที่ — คอลัมน์ที่ได้: {list(df.columns)}")


def _disease_cols(df, colmap):
    """คืน dict ชื่อคอลัมน์ดิบ → ชื่อโรค"""
    low = {c.lower().strip(): c for c in df.columns}
    out = {}
    for k, v in colmap.items():
        if k.lower() in low: out[low[k.lower()]] = v
    for c in df.columns:                                   # ถ้าคอลัมน์เป็นชื่อโรคอยู่แล้ว
        if c in DISEASE_COLS and c not in out: out[c] = c
    return out


def to_tambon(df, colmap=COLMAP, by=()):
    """รวมแถวดิบ (hospcode × areacode) เป็นรายตำบล — by = คอลัมน์เพิ่มเติม เช่น เดือน"""
    if df.empty: return pd.DataFrame()
    area = _area_col(df); dmap = _disease_cols(df, colmap)
    if not dmap: raise RuntimeError(f"ไม่พบคอลัมน์โรค (r1_1 … r6 หรือชื่อโรค) — คอลัมน์ที่ได้: {list(df.columns)}")
    d = df.copy()
    d["a_code"] = d[area].astype(str).str.replace(r"\.0$", "", regex=True).str.zfill(8).str[:6]
    d = d[d["a_code"].str[:2] == PROVINCE]
    for c in dmap: d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    g = d.groupby(["a_code", *by])[list(dmap)].sum().rename(columns=dmap)
    g = g.T.groupby(level=0).sum().T                       # รวมคอลัมน์ชื่อซ้ำ (ถ้ามี)
    for c in DISEASE_COLS:
        if c not in g: g[c] = 0
    g["total"] = g[DISEASE_COLS].sum(axis=1)
    return g.reset_index()


def finish(g, fy, month, names):
    y_be, y_ce = fy_month_to_calendar(fy, month)
    g = g.copy()
    g["fy_be"], g["month"], g["year_be"] = y_be + (1 if month >= 10 else 0), month, y_be
    g["ym"] = f"{y_ce:04d}-{month:02d}"
    nm = g["a_code"].map(names)
    g["a_name"] = nm.map(lambda v: (v.get("th") or v.get("en") or "") if isinstance(v, dict) else ("" if pd.isna(v) else str(v)))
    return g


# ---------------------------------------------------------------- การตรวจผล
def validate(monthly, annual_totals):
    """ผลรวม 12 เดือนต้องเท่ากับยอดรายปีงบ และค่ารายเดือนต้องไม่เท่ากับยอดทั้งปีทุกเดือน"""
    ok = True
    s = monthly.groupby("year_be")["total"].sum()
    rows = []
    for fy, tot in annual_totals.items():
        m = monthly[monthly.year_be == fy]
        if m.empty: continue
        per_m = m.groupby("month")["total"].sum()
        same_as_year = (per_m == tot).sum()
        rows.append({"year_be": fy, "annual": tot, "sum_monthly": int(s.get(fy, 0)), "months": per_m.size,
                     "diff_%": round((s.get(fy, 0) - tot) / tot * 100, 2) if tot else None,
                     "months_equal_annual": int(same_as_year)})
        if same_as_year >= 2:
            ok = False; print(f"✗ ปี {fy}: มี {same_as_year} เดือนที่ยอดเท่ากับทั้งปี → API ไม่ได้กรองตามเดือน")
    rep = pd.DataFrame(rows)
    if len(rep): print("\n=== ตรวจผล: ผลรวมรายเดือนเทียบยอดรายปีงบ ===\n" + rep.to_string(index=False))
    full = rep[rep.months == 12] if len(rep) else rep
    if len(full) and (full["diff_%"].abs() > 3).any():
        ok = False; print("✗ ผลรวม 12 เดือนต่างจากยอดรายปีเกิน 3% — ตรวจพารามิเตอร์เดือน/ปีอีกครั้ง")
    elif len(full) and (full["diff_%"].abs() > 1).any():
        print("⚠ บางปีต่างจากยอดรายปี 1–3% — มักเกิดจากเดือน ธ.ค. ที่สองตารางหยุดปรับปรุงไม่พร้อมกัน (ดู flag_incomplete)")
    return ok, rep


def annual_totals(fys):
    out = {}
    for fy in fys:
        try:
            t = to_tambon(fetch_opendata(fy, table=TABLE)); out[fy] = int(t.total.sum())     # ยอดรายปีจาก s_pm25_disease
        except Exception as e:
            print(f"   ⚠ ยอดรายปีงบ {fy} ดึงไม่ได้: {str(e)[:80]}")
    return out


# ---------------------------------------------------------------- วิธีที่ 1: Open Data
def months_from_raw(raw):
    """ถ้าข้อมูลดิบมีมิติเดือน คืนชื่อคอลัมน์เดือน (สร้างจากวันที่ถ้าจำเป็น)"""
    for c in raw.columns:
        if re.fullmatch(MONTH_COL_PAT, c.lower()): return c
    for c in raw.columns:
        if re.fullmatch(DATE_COL_PAT, c.lower()):
            raw["_month"] = pd.to_datetime(raw[c].astype(str), errors="coerce").dt.month
            if raw["_month"].notna().mean() > 0.9: return "_month"
    return None


def wide_months_to_long(raw, year_is_calendar=True):
    """รูปแบบรายงานรายเดือน: 1 แถวต่อ (พื้นที่ × โรค) มีคอลัมน์ m1…m12 → แถวต่อ (พื้นที่ × เดือน) คอลัมน์ละโรค"""
    mcols = [c for c in raw.columns if re.fullmatch(MCOL, c.lower())]
    dcol = next((c for c in raw.columns if raw[c].astype(str).str.lower().str.strip().isin(NAME_ALIASES).mean() > 0.5), None)
    if not mcols or dcol is None: return None
    d = raw.copy(); d["_dis"] = d[dcol].astype(str).str.lower().str.strip().map(NAME_ALIASES)
    d = d[d._dis.notna()]
    idv = [c for c in d.columns if c not in mcols + [dcol, "_dis", "total"] and not re.fullmatch(r"r\d+(_\d+)?", c.lower())]
    L = d.melt(id_vars=idv + ["_dis"], value_vars=mcols, var_name="_m", value_name="_v")
    L["month"] = L._m.str.extract(r"(\d+)").astype(int)
    L["_v"] = pd.to_numeric(L._v, errors="coerce").fillna(0)
    W = L.pivot_table(index=idv + ["month"], columns="_dis", values="_v", aggfunc="sum", fill_value=0).reset_index()
    W.columns.name = None
    return W


GROUP_MAP = {}          # (disease_group_id, disease_sub_group_id) → r-code (หาอัตโนมัติจากยอดรายปี)


def _gkey(g, sg):
    g = str(g).strip().replace(".0", ""); sg = "" if pd.isna(sg) else str(sg).strip().replace(".0", "")
    return g, sg


def infer_group_map(raw_m, year):
    """จับคู่ (disease_group_id, disease_sub_group_id) กับคอลัมน์ r1_1…r6 ของ s_pm25_disease ด้วยยอดรวมทั้งปีของจังหวัด
    (ยอดของแต่ละโรคไม่ซ้ำกัน จึงจับคู่ได้แน่นอน) ถ้าจับคู่ไม่ได้ ใช้สมมติฐาน r{group}_{sub}"""
    mcols = [c for c in raw_m.columns if re.fullmatch(MCOL, c.lower())]
    d = raw_m.copy()
    d["a6"] = d["areacode"].astype(str).str.zfill(8).str[:6]; d = d[d.a6.str[:2] == PROVINCE]
    for c in mcols: d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
    d["_k"] = [_gkey(g, sg) for g, sg in zip(d.disease_group_id, d.disease_sub_group_id)]
    mt = d.groupby("_k")[mcols].sum().sum(axis=1)
    ann = fetch_opendata(year, table=TABLE)
    ann = ann[ann["areacode"].astype(str).str.zfill(8).str[:2] == PROVINCE]
    at = {c.lower(): pd.to_numeric(ann[c], errors="coerce").fillna(0).sum() for c in ann.columns if c.lower() in COLMAP}
    out, used = {}, set()
    for k, v in mt.items():
        hit = [rc for rc, av in at.items() if abs(av - v) < 0.5 and rc not in used]
        if len(hit) == 1:
            out[k] = hit[0]; used.add(hit[0]); continue
        g, sg = k
        guess = f"r{g}_{sg}" if sg not in ("", "0") and f"r{g}_{sg}" in COLMAP else f"r{g}"
        out[k] = guess if guess in COLMAP else None
    rows = [{"group": k[0], "sub": k[1], "total_month_table": int(mt[k]), "→": out[k], "disease": COLMAP.get(out[k]),
             "total_s_pm25_disease": int(at.get(out[k], -1)) if out[k] else None} for k in mt.index]
    print(f"\n=== จับคู่รหัสกลุ่มโรคกับคอลัมน์ r (ปี {year}) ===\n" + pd.DataFrame(rows).to_string(index=False))
    bad = [r for r in rows if r["→"] is None or r["total_s_pm25_disease"] != r["total_month_table"]]
    if bad:
        print("⚠ บางกลุ่มยอดไม่ตรงกับ s_pm25_disease — ตรวจตารางด้านบน (การตรวจผลรวมท้ายสคริปต์จะยืนยันอีกครั้ง)")
    GROUP_MAP.update(out)


def month_columns_to_tambon(raw):
    """แปลงข้อมูลที่มีเดือนเป็นคอลัมน์ → ตำบล × เดือน × โรค
    รองรับ (ก) 1 แถวต่อ (พื้นที่ × โรค) + m1…m12   (ข) คอลัมน์โรค×เดือน เช่น r1_1_m1 หรือ m1_r1_1"""
    if {"disease_group_id", "disease_sub_group_id"} <= set(raw.columns):
        mcols = [c for c in raw.columns if re.fullmatch(MCOL, c.lower())]
        d = raw.copy()
        d["_rc"] = [GROUP_MAP.get(_gkey(g, sg)) for g, sg in zip(d.disease_group_id, d.disease_sub_group_id)]
        unk = d._rc.isna().sum()
        if unk: print(f"   ⚠ {unk} แถวที่จับคู่รหัสโรคไม่ได้ — ตัดออก")
        d = d[d._rc.notna()]
        L = d.melt(id_vars=["areacode", "_rc"], value_vars=mcols, var_name="_m", value_name="_v")
        L["month"] = L._m.str.extract(r"(\d+)", expand=False).astype(int)
        L["_v"] = pd.to_numeric(L._v, errors="coerce").fillna(0)
        W = L.pivot_table(index=["areacode", "month"], columns="_rc", values="_v", aggfunc="sum", fill_value=0).reset_index()
        W.columns.name = None
        return to_tambon(W, by=("month",))
    W = wide_months_to_long(raw)
    if W is not None:
        return to_tambon(W, by=("month",))
    pat = re.compile(r"^(?:(r\d+(?:_\d+)?)_?m(\d{1,2})|m(\d{1,2})_?(r\d+(?:_\d+)?))$", re.I)
    pieces = {}
    for c in raw.columns:
        mt = pat.match(c)
        if mt:
            rc = (mt.group(1) or mt.group(4)).lower(); m = int(mt.group(2) or mt.group(3))
            pieces.setdefault(m, {})[c] = rc
    if not pieces:
        raise RuntimeError(f"มีคอลัมน์ m1…m12 แต่ไม่รู้ว่าแถวไหนเป็นโรคอะไร — ส่งผล --probe ให้ผู้พัฒนาสคริปต์ (คอลัมน์: {list(raw.columns)})")
    base = [c for c in raw.columns if not pat.match(c)]
    out = []
    for m, cmap in sorted(pieces.items()):
        sub = raw[base + list(cmap)].rename(columns=cmap)
        out.append(to_tambon(sub).assign(month=m))
    return pd.concat(out, ignore_index=True)


def run_opendata(fys, names, table=MONTHLY_TABLE):
    frames = []
    raw0 = fetch_opendata(fys[0], table=table)
    print(f"ตาราง {table} — คอลัมน์ดิบ: {list(raw0.columns)}")
    if wide_months_to_long(raw0) is not None or any(re.fullmatch(MCOL, c.lower()) or re.fullmatch(r"(r\d+(_\d+)?_?m\d{1,2}|m\d{1,2}_?r\d+(_\d+)?)", c.lower()) for c in raw0.columns):
        print("✓ ข้อมูลมีคอลัมน์รายเดือน m1…m12")
        if {"disease_group_id", "disease_sub_group_id"} <= set(raw0.columns):
            full_year = next((y for y in fys if y < dt.date.today().year + 543), fys[0])
            infer_group_map(raw0 if full_year == fys[0] else fetch_opendata(full_year, table=table), full_year)
        for fy in fys:
            raw = raw0 if fy == fys[0] else fetch_opendata(fy, table=table)
            if raw.empty: print(f"   ปี {fy}: ไม่มีข้อมูล"); continue
            g = month_columns_to_tambon(raw)
            for m, gm in g.groupby("month"):
                if gm[DISEASE_COLS].values.sum() > 0:
                    frames.append(finish(gm.drop(columns="month"), fy, int(m), names))
            print(f"   ปี {fy}: ✓ {len(raw):,} แถวดิบ → {g.a_code.nunique()} ตำบล, เดือนที่มีข้อมูล {sorted(g[g[DISEASE_COLS].sum(axis=1) > 0].month.unique().tolist())}")
            time.sleep(0.5)
        return pd.concat(frames, ignore_index=True)
    mcol = months_from_raw(raw0)
    if mcol:
        print(f"✓ ข้อมูลดิบมีมิติเดือน ({mcol}) — รวมตามเดือนได้โดยตรง")
        for fy in fys:
            raw = raw0 if fy == fys[0] else fetch_opendata(fy, table=table)
            mc = months_from_raw(raw)
            raw[mc] = pd.to_numeric(raw[mc], errors="coerce")
            g = to_tambon(raw, by=(mc,)).rename(columns={mc: "month"})
            for m, gm in g.groupby("month"):
                frames.append(finish(gm.drop(columns="month"), fy, int(m), names))
            print(f"   ปีงบ {fy}: ✓ {g.month.nunique()} เดือน")
        return pd.concat(frames, ignore_index=True)
    print("ℹ ข้อมูลดิบไม่มีคอลัมน์เดือน → ลองส่งพารามิเตอร์เดือนให้ API")
    ann = int(to_tambon(raw0).total.sum())
    for key in ("month", "b_month", "mm"):
        tots = {}
        for m in (10, 11, 1, 4):
            try:
                tots[m] = int(to_tambon(fetch_opendata(fys[0], {key: str(m)}, table=table)).total.sum())
            except Exception as e:
                tots[m] = None
        print(f"   พารามิเตอร์ '{key}': ยอดเดือนทดสอบ {tots} (ยอดทั้งปี {ann:,})")
        vals = [v for v in tots.values() if v is not None]
        if len(vals) >= 3 and len(set(vals)) > 1 and all(v < ann for v in vals):
            print(f"✓ API กรองตามเดือนด้วย '{key}'")
            for fy in fys:
                for m in FY_MONTHS:
                    try:
                        g = to_tambon(fetch_opendata(fy, {key: str(m)}, table=table))
                    except Exception as e:
                        print(f"   ✗ ปีงบ {fy} เดือน {m}: {str(e)[:80]}"); continue
                    if len(g): frames.append(finish(g, fy, m, names))
                    time.sleep(0.4)
                print(f"   ปีงบ {fy}: ✓")
            return pd.concat(frames, ignore_index=True)
    sys.exit("\n✗ MOPH Open Data (s_pm25_disease) ไม่มีข้อมูลรายเดือน และไม่รับพารามิเตอร์เดือน\n"
             "  → ใช้วิธีที่ 2 (--source template จากหน้ารายงาน HDC) หรือวิธีที่ 3 (--source files) — ดูคำอธิบายบนสุดของไฟล์")


# ---------------------------------------------------------------- วิธีที่ 2: template จากหน้ารายงาน HDC
TEMPLATE_EXAMPLE = {
    "_คำอธิบาย": "คัดลอก URL / method / headers / payload จาก DevTools (F12 → Network) ของหน้ารายงานที่เลือก 1 เดือน "
                 "แล้วแทนปี/เดือนด้วย {fy} {month} {mm} {year_be} {year_ce} {yyyymm_ce} {yyyymm_be}",
    "url": "https://api-hdc.moph.go.th/....(คัดลอกจาก DevTools)",
    "method": "POST",
    "headers": {"Content-Type": "application/json", "Authorization": "Bearer null", "Origin": "https://hdc.moph.go.th"},
    "params": {},
    "body": {"(ชื่อฟิลด์ปี)": "{fy}", "(ชื่อฟิลด์เดือน)": "{mm}", "province_code": "19", "table_display": "tambon"},
    "colmap": {"r1_1": "COPD"},
}


def _fill(obj, ctx):
    if isinstance(obj, str):
        try: return obj.format(**ctx)
        except (KeyError, IndexError, ValueError): return obj
    if isinstance(obj, dict): return {k: _fill(v, ctx) for k, v in obj.items() if not k.startswith("_")}
    if isinstance(obj, list): return [_fill(v, ctx) for v in obj]
    return obj


def _rows_from_json(js):
    """หา list ของ dict ที่ใหญ่ที่สุดใน response"""
    best = []
    def walk(o):
        nonlocal best
        if isinstance(o, list) and o and all(isinstance(x, dict) for x in o) and len(o) > len(best): best = o
        if isinstance(o, dict): [walk(v) for v in o.values()]
        elif isinstance(o, list): [walk(v) for v in o]
    walk(js)
    return pd.DataFrame(best)


def run_template(path, fys, names):
    T = json.load(open(path, encoding="utf-8"))
    colmap = {**COLMAP, **T.get("colmap", {})}
    frames, shown = [], False
    for fy in fys:
        for m in FY_MONTHS:
            y_be, y_ce = fy_month_to_calendar(fy, m)
            ctx = dict(fy=fy, month=m, mm=f"{m:02d}", year_be=y_be, year_ce=y_ce,
                       yyyymm_ce=f"{y_ce}{m:02d}", yyyymm_be=f"{y_be}{m:02d}")
            url, params = _fill(T["url"], ctx), _fill(T.get("params", {}), ctx)
            headers, body = _fill(T.get("headers", {}), ctx), _fill(T.get("body"), ctx)
            try:
                if T.get("method", "POST").upper() == "GET":
                    r = requests.get(url, params=params, headers=headers, timeout=(15, 180))
                else:
                    r = requests.post(url, params=params, headers=headers, json=body, timeout=(15, 180))
                if r.status_code not in (200, 201): raise RuntimeError(f"HTTP {r.status_code}: {r.text[:150]}")
                raw = _rows_from_json(r.json())
                if not shown: print(f"คอลัมน์ดิบ (template): {list(raw.columns)}"); shown = True
                g = to_tambon(raw, colmap)
            except Exception as e:
                print(f"   ✗ ปีงบ {fy} เดือน {m}: {str(e)[:120]}"); continue
            if len(g): frames.append(finish(g, fy, m, names))
            time.sleep(0.5)
        print(f"   ปีงบ {fy}: ✓ {sum(f.fy_be.iloc[0] == fy for f in frames)} เดือน")
    if not frames: sys.exit("✗ ไม่ได้ข้อมูลจาก template — ตรวจ URL/headers/payload")
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------- วิธีที่ 3: ไฟล์ที่ดาวน์โหลดเอง
def run_files(folder, names):
    frames = []
    for f in sorted(glob.glob(os.path.join(folder, "*.*"))):
        m_ = re.search(r"(25\d{2})\D{0,3}(\d{1,2})", os.path.basename(f))
        if not m_ or not f.lower().endswith((".csv", ".xlsx", ".xls")):
            print(f"   ข้าม {os.path.basename(f)} (ชื่อไฟล์ต้องมี ปีงบ_เดือน เช่น 2567_10.xlsx)"); continue
        fy, m = int(m_.group(1)), int(m_.group(2))
        raw = pd.read_excel(f) if f.lower().endswith(("xlsx", "xls")) else pd.read_csv(f, encoding="utf-8-sig")
        try:
            g = to_tambon(raw)
        except Exception as e:
            print(f"   ✗ {os.path.basename(f)}: {str(e)[:120]}"); continue
        frames.append(finish(g, fy, m, names)); print(f"   ✓ {os.path.basename(f)}: ปีงบ {fy} เดือน {m}, {len(g)} ตำบล")
    if not frames: sys.exit("✗ ไม่พบไฟล์ที่อ่านได้")
    return pd.concat(frames, ignore_index=True)


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="ดึง HDC s_pm25_disease จังหวัดสระบุรี รายตำบล รายเดือน")
    ap.add_argument("--start", type=int, default=2565, help="ปีงบเริ่มต้น (พ.ศ.)")
    ap.add_argument("--end", type=int, default=dt.date.today().year + 543, help="ปีสุดท้าย (ปีปฏิทิน พ.ศ.)")
    ap.add_argument("--source", choices=["opendata", "template", "files"], default="opendata")
    ap.add_argument("--template", default="hdc_request_template.json")
    ap.add_argument("--files-dir", default="hdc_monthly_downloads")
    ap.add_argument("--out", default=None)
    ap.add_argument("--names", default=None, help="CSV เดิม (a_code, a_name) สำหรับเติมชื่อตำบล")
    ap.add_argument("--table", default=MONTHLY_TABLE, help="ชื่อตาราง Open Data (ค่าเริ่มต้น s_pm25_month = รายงานรายเดือน)")
    ap.add_argument("--probe", action="store_true", help="แสดงคอลัมน์และ 5 แถวแรกของข้อมูลดิบ Open Data แล้วจบ")
    ap.add_argument("--make-template", action="store_true", help="พิมพ์ตัวอย่างไฟล์ template แล้วจบ")
    ap.add_argument("--annual", action="store_true", help="บันทึกแบบรายปีงบ (แบบเดิม)")
    ap.add_argument("--no-validate", action="store_true", help="ไม่ตรวจเทียบยอดรายปีงบ (ไม่แนะนำ)")
    a = ap.parse_args()

    if a.make_template:
        with open("hdc_request_template.json", "w", encoding="utf-8") as f:
            json.dump(TEMPLATE_EXAMPLE, f, ensure_ascii=False, indent=2)
        print("✓ เขียน hdc_request_template.json — แก้ url/headers/body ตาม DevTools แล้วรัน --source template"); return
    fys = list(range(a.start, a.end + 1))
    if a.probe:
        raw = fetch_opendata(fys[-1], table=a.table)
        print(f"ตาราง {a.table} ปี {fys[-1]}: {len(raw)} แถวดิบ\nคอลัมน์: {list(raw.columns)}\n{raw.head(8).to_string()}")
        mc = [c for c in raw.columns if re.fullmatch(MCOL, c.lower())]
        print(f"\nคอลัมน์เดือน: {months_from_raw(raw) or (mc if mc else 'ไม่มี')}"); return

    names = load_names(a.names)
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M")
    if a.annual:
        frames = [to_tambon(fetch_opendata(fy)).assign(year=fy) for fy in fys]
        res = pd.concat(frames, ignore_index=True); res["a_name"] = res.a_code.map(names).fillna("")
        out = a.out or f"hdc_saraburi_pm25_disease_tambon_{a.start}_{a.end}_{stamp}.csv"
        res.to_csv(out, index=False, encoding="utf-8-sig"); print(f"✓ บันทึก {out}"); return

    if a.source == "opendata": res = run_opendata(fys, names, table=a.table)
    elif a.source == "template": res = run_template(a.template, fys, names)
    else: res = run_files(a.files_dir, names)

    res = res.groupby(["a_code", "a_name", "fy_be", "year_be", "month", "ym"], as_index=False)[DISEASE_COLS + ["total"]].sum()
    res["total_11"] = res[ELEVEN].sum(axis=1)                      # 11 โรคที่ใช้วิเคราะห์ (ไม่รวม r5, r6)
    res = res.sort_values(["ym", "a_code"])
    # ธ.ค. ของทุกปีถูกบันทึกไม่ครบ: ตาราง HDC รายปีหยุดปรับปรุงช่วงต้น ม.ค. ของปีถัดไป (ยอด ธ.ค. ≈ 15–35% ของเดือนปกติ)
    res["flag_incomplete"] = (res.month == 12).astype(int)
    pm_ = res.pivot_table(index="month", columns="year_be", values="total_11", aggfunc="sum")
    print("\nยอดรวมจังหวัดรายเดือน (11 โรค) — ตรวจเดือนที่ต่ำผิดปกติ:\n" + pm_.to_string())

    if not a.no_validate:
        ok, rep = validate(res, annual_totals(sorted(res.year_be.unique())))
        if not ok:
            bad = (a.out or "hdc_monthly").replace(".csv", "") + "_FAILED_CHECK.csv"
            res.to_csv(bad, index=False, encoding="utf-8-sig")
            sys.exit(f"\n✗ ไม่ผ่านการตรวจ — บันทึกไว้ที่ {bad} เพื่อตรวจสอบเท่านั้น (อย่านำไปวิเคราะห์)")

    out = a.out or f"hdc_saraburi_pm25_disease_tambon_monthly_{a.start}_{a.end}_{stamp}.csv"
    res.to_csv(out, index=False, encoding="utf-8-sig")
    json.dump({"source": a.source, "table": TABLE, "province": PROVINCE, "downloaded_at": dt.datetime.now().isoformat(),
               "months": int(res.ym.nunique()), "tambons": int(res.a_code.nunique())},
              open(out.replace(".csv", "_meta.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"\n✓ บันทึก {out} ({len(res):,} แถว = {res.a_code.nunique()} ตำบล × {res.ym.nunique()} เดือน, {res.ym.min()} ถึง {res.ym.max()})")
    print("  อัปโหลดไป Drive แล้วตั้ง HDC_MONTHLY_CSV ใน notebooks/11 และ 14 เป็น path ของไฟล์นี้")
    print("\nสรุปรายเดือน (11 โรค):\n" + res.groupby("ym")["total_11"].sum().to_string())


if __name__ == "__main__":
    main()
