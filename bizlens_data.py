"""Pemuat data BizLens: membaca langsung dari biz_lens_data.xlsx.

Cukup edit Excel-nya lalu refresh app. Cache otomatis diperbarui setiap kali
file Excel berubah (dicek dari waktu terakhir file disimpan).
"""
import math
import re
from pathlib import Path

import pandas as pd
import streamlit as st

EXCEL_FILE = Path(__file__).resolve().parent / "biz_lens_data.xlsx"

# Sheet dan kolom wajib yang dibutuhkan app
REQUIRED = {
    "cities": ["slug", "nama", "provinsi", "cpi_score", "cpi_tier", "cpi_tier_batas", "ringkasan",
               "populasi", "populasi_peringkat", "populasi_avg_nasional",
               "pdrb_t", "pdrb_tumbuh", "pdrb_tumbuh_nasional",
               "pdrb_kapita_jt", "pdrb_kapita_peringkat", "pdrb_kapita_nasional_jt",
               "usia_produktif", "usia_produktif_peringkat", "usia_produktif_nasional",
               "cabang_ocbc", "penetrasi_bank", "jumlah_umkm", "jumlah_korporasi",
               "dpk_t", "tabungan_t", "giro_t", "kredit_t", "kredit_konsumer_t", "kredit_umkm_t",
               "jalan_tol", "bandara"],
    "city_dims": ["slug", "dimensi", "skor"],
    "city_banks": ["slug", "kelompok", "cabang"],
    "branches": ["slug", "nama", "kota", "mpi_tier", "mpi_score", "internal_tier",
                 "internal_score", "overlap_tier", "overlap_score"],
    "branch_mpi": ["slug", "komponen", "skor"],
    "branch_internal": ["slug", "komponen", "tier"],
    "branch_nearest": ["slug", "komponen", "tier"],
    "branch_context": ["slug", "kategori", "item", "jumlah"],
    "branch_overlap": ["slug", "type", "r_2km", "r_2_5km", "r_5_10km"],
    "neighbors": ["branch_slug", "radius_group", "nama", "type", "radius", "performance", "mpi"],
    "tier_cps": ["tier", "rentang", "jumlah_kota", "kota_hadir", "kota_standalone", "cabang"],
    "tier_mps": ["tier", "rentang", "cabang"],
    "regional": ["kode", "nama", "jumlah_kota", "cps_rata", "kota_hadir", "cabang"],
    "overlap_heatmap": ["mps_urut", "mps_label", "cps_urut", "cps_label", "nilai", "kategori"],
    "proposal_cabang": ["kategori_id", "warna", "kategori", "deskripsi", "total", "catatan"],
    "proposal_dist": ["kategori_id", "tier", "jumlah"],
    "proposal_action": ["kategori_id", "aksi", "tier", "jumlah"],
}


class ExcelDataError(Exception):
    """Excel tidak sesuai format yang dibutuhkan app."""


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------
def _clean(v):
    """NaN/kosong -> None, angka numpy -> angka Python, 81.0 -> 81."""
    if v is None:
        return None
    if hasattr(v, "item"):  # numpy scalar
        v = v.item()
    if isinstance(v, float):
        if math.isnan(v):
            return None
        if v.is_integer():
            return int(v)
    if isinstance(v, str):
        v = v.strip()
        return v or None
    return v


def _records(df):
    return [{k: _clean(v) for k, v in row.items()} for row in df.to_dict(orient="records")]


def _group_dict(rows, key, name, value):
    out = {}
    for r in rows:
        if r[key] is None or r[name] is None:
            continue
        out.setdefault(r[key], {})[r[name]] = r[value]
    return out


def _read_all_sheets():
    if not EXCEL_FILE.exists():
        raise ExcelDataError(
            f"File **{EXCEL_FILE.name}** tidak ditemukan. Letakkan file Excel di folder yang sama "
            f"dengan `app.py` ({EXCEL_FILE.parent})."
        )
    try:
        xl = pd.ExcelFile(EXCEL_FILE, engine="openpyxl")
    except Exception as e:  # file rusak / sedang dibuka & terkunci
        raise ExcelDataError(f"File **{EXCEL_FILE.name}** tidak bisa dibuka: {e}")

    missing_sheets = [s for s in REQUIRED if s not in xl.sheet_names]
    if missing_sheets:
        raise ExcelDataError(
            "Sheet berikut tidak ditemukan di Excel: "
            + ", ".join(f"`{s}`" for s in missing_sheets)
            + ". Pastikan nama sheet tidak diubah."
        )

    sheets = {}
    problems = []
    for name, cols in REQUIRED.items():
        df = xl.parse(name)
        df.columns = [str(c).strip() for c in df.columns]
        missing_cols = [c for c in cols if c not in df.columns]
        if missing_cols:
            problems.append(f"- Sheet `{name}`: kolom " + ", ".join(f"`{c}`" for c in missing_cols) + " tidak ada")
        df = df.dropna(how="all")  # buang baris kosong
        sheets[name] = _records(df)
    if problems:
        raise ExcelDataError("Kolom wajib tidak lengkap:\n" + "\n".join(problems))

    # Sheet opsional `info` (kolom: kunci, nilai) — misalnya periode data
    sheets["info"] = []
    if "info" in xl.sheet_names:
        df = xl.parse("info")
        df.columns = [str(c).strip().lower() for c in df.columns]
        if {"kunci", "nilai"} <= set(df.columns):
            sheets["info"] = _records(df.dropna(how="all"))
    return sheets


# ------------------------------------------------------------------
# Builders (Excel -> struktur yang dipakai halaman)
# ------------------------------------------------------------------
def _build_kota(s):
    dims = _group_dict(s["city_dims"], "slug", "dimensi", "skor")
    banks = _group_dict(s["city_banks"], "slug", "kelompok", "cabang")
    out = {}
    for r in s["cities"]:
        slug = r.pop("slug")
        if slug is None:
            continue
        r["skor_dimensi"] = dims.get(slug, {})
        r["cabang_bank"] = banks.get(slug, {})
        out[slug] = r
    return out


def _build_cabang(s):
    mpi = _group_dict(s["branch_mpi"], "slug", "komponen", "skor")
    internal = _group_dict(s["branch_internal"], "slug", "komponen", "tier")
    nearest = _group_dict(s["branch_nearest"], "slug", "komponen", "tier")

    ctx = {}
    for r in s["branch_context"]:
        if None in (r["slug"], r["kategori"], r["item"]):
            continue
        ctx.setdefault(r["slug"], {}).setdefault(str(r["kategori"]).lower(), {})[r["item"]] = r["jumlah"]

    overlap = {}
    for r in s["branch_overlap"]:
        slug = r.pop("slug")
        if slug is not None:
            overlap.setdefault(slug, []).append(r)

    nbrs = {"lt_2km": {}, "2_5km": {}}
    for r in s["neighbors"]:
        slug, grp = r.pop("branch_slug"), r.pop("radius_group")
        if slug is not None and grp in nbrs:
            nbrs[grp].setdefault(slug, []).append(r)

    out = {}
    for r in s["branches"]:
        slug = r.pop("slug")
        if slug is None:
            continue
        c = ctx.get(slug, {})
        near = dict(nearest.get(slug, {}))
        near.setdefault("nama", "–")
        r.update({
            "mpi_components": mpi.get(slug, {}),
            "internal_components": internal.get(slug, {}),
            "nearest_branch": near,
            "commercial_density": c.get("commercial", {}),
            "competition": c.get("competition", {}),
            "demographic": c.get("demographic", {}),
            "economic_hub": c.get("economic", {}),
            "overlap_summary": overlap.get(slug, []),
            "neighbors_lt_2km": nbrs["lt_2km"].get(slug, []),
            "neighbors_2_5km": nbrs["2_5km"].get(slug, []),
        })
        out[slug] = r
    return out


def _build_tier(s):
    dist = _group_dict(s["proposal_dist"], "kategori_id", "tier", "jumlah")
    act = {}
    for r in s["proposal_action"]:
        if None in (r["kategori_id"], r["aksi"], r["tier"]):
            continue
        act.setdefault(r["kategori_id"], {}).setdefault(str(r["aksi"]).lower(), {})[r["tier"]] = r["jumlah"]
    proposal = []
    for r in s["proposal_cabang"]:
        kid = r["kategori_id"]
        if kid is None:
            continue
        r["dist_cps"] = dist.get(kid, {})
        r["close"] = act.get(kid, {}).get("close", {})
        r["review"] = act.get(kid, {}).get("review", {})
        proposal.append(r)
    return {
        "tier_distribution_cps": s["tier_cps"],
        "tier_distribution_mps": s["tier_mps"],
        "regional": s["regional"],
        "overlap_heatmap": s["overlap_heatmap"],
        "proposal_cabang": proposal,
    }


@st.cache_data(show_spinner="Membaca data Excel…", max_entries=2)
def _load_all(file_mtime: float) -> dict:
    """Dibaca ulang otomatis setiap kali waktu simpan Excel berubah.

    `file_mtime` sengaja tanpa awalan "_" supaya ikut jadi kunci cache.
    """
    s = _read_all_sheets()
    info = {str(r["kunci"]).strip().lower(): r["nilai"] for r in s["info"] if r.get("kunci") is not None}
    return {"kota": _build_kota(s), "cabang": _build_cabang(s), "tier": _build_tier(s), "info": info}


def _data() -> dict:
    try:
        mtime = EXCEL_FILE.stat().st_mtime if EXCEL_FILE.exists() else 0.0
        return _load_all(mtime)
    except ExcelDataError as e:
        st.error(f"**Data Excel bermasalah.**\n\n{e}")
        st.stop()
    except Exception as e:
        st.error(f"**Gagal membaca data Excel:** {e}")
        st.stop()


def load_kota(required: bool = True) -> dict:
    d = _data()["kota"]
    if not d and required:
        st.warning("Sheet `cities` masih kosong. Tambahkan minimal satu kota di Excel.")
        st.stop()
    return d


def load_cabang(required: bool = True) -> dict:
    d = _data()["cabang"]
    if not d and required:
        st.warning("Sheet `branches` masih kosong. Tambahkan minimal satu cabang di Excel.")
        st.stop()
    return d


def load_tier() -> dict:
    return _data()["tier"]


def load_info() -> dict:
    """Isi sheet opsional `info`, misalnya {'periode': 'EOY 2025'}."""
    return _data()["info"]


def periode_text(prefix: str = "", suffix: str = "") -> str:
    """Teks periode data dari sheet `info` (kunci `periode`); kosong kalau tidak diisi."""
    p = load_info().get("periode")
    return f"{prefix}{p}{suffix}" if p else ""


def footer():
    """Caption bawah halaman dengan periode data dari Excel."""
    st.markdown("---")
    st.caption("© OCBC NISP · BizLens" + periode_text(" · Data per "))


# ------------------------------------------------------------------
# Tier helpers
# ------------------------------------------------------------------
def _tier_key(row):
    nums = re.findall(r"\d+", str(row.get("tier") or ""))
    return int(nums[0]) if nums else 999


def sorted_tiers(rows: list) -> list:
    """Urutkan baris tier berdasarkan angka di nama tier (Tier 1, Tier 2, …)."""
    return sorted(rows, key=_tier_key)


def tier_threshold(rows: list):
    """Batas bawah tier teratas, diambil dari kolom `rentang` (mis. '>70' -> 70)."""
    rows = sorted_tiers(rows)
    if not rows:
        return None
    nums = re.findall(r"\d+(?:\.\d+)?", str(rows[0].get("rentang") or ""))
    return float(nums[0]) if nums else None


def tier_range_text(rows: list) -> str:
    """Mis. 'Tier 1 (>70), Tier 2 (>50-70), …' dari data."""
    return ", ".join(f"{r['tier']} ({r['rentang']})" for r in sorted_tiers(rows) if r.get("tier"))


# ------------------------------------------------------------------
# Format helpers
# ------------------------------------------------------------------
def fmt_bulat(n) -> str:
    if n is None:
        return "–"
    return f"{int(round(n)):,}".replace(",", ".")


def fmt_pct(n, digits: int = 0) -> str:
    if n is None:
        return "–"
    return f"{n * 100:.{digits}f}%"


def fmt_rp_t(n) -> str:
    if n is None:
        return "–"
    return f"Rp{n:.1f} T"


def fmt_rp_jt(n) -> str:
    if n is None:
        return "–"
    return f"Rp{n:.1f} jt"


def fmt_jt(n) -> str:
    if n is None:
        return "–"
    return f"{n / 1e6:.1f} jt"
