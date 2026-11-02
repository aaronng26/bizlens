"""BizLens homepage. Semua angka dihitung dari biz_lens_data.xlsx."""
import html

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from styling import section_header, kpi_card, OCBC_RED, OCBC_RED_3, OCBC_RED_SOFT
from bizlens_data import (
    load_tier, load_kota, load_cabang, load_info, periode_text, footer,
    sorted_tiers, tier_range_text, fmt_bulat, fmt_pct,
)


def esc(v) -> str:
    """Teks dari Excel aman ditaruh di HTML."""
    return html.escape("" if v is None else str(v))


def num(v) -> float:
    return v if isinstance(v, (int, float)) else 0


def ratio(a, b):
    return a / b if b else None


def tier_span_label(rows) -> str:
    """Mis. ['Tier 1','Tier 2'] -> 'Tier 1–2'."""
    names = [str(r.get("tier") or "") for r in rows]
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    a, b = names[0], names[-1]
    pa, pb = a.rsplit(" ", 1), b.rsplit(" ", 1)
    if len(pa) == 2 and len(pb) == 2 and pa[0] == pb[0]:
        return f"{pa[0]} {pa[1]}–{pb[1]}"
    return f"{a}–{b}"


# ============================================================
# Data
# ============================================================
tier = load_tier()
info = load_info()
kota_all = load_kota(required=False)
cabang_all = load_cabang(required=False)

cps_rows = sorted_tiers(tier["tier_distribution_cps"])
mps_rows = sorted_tiers(tier["tier_distribution_mps"])
proposal = tier["proposal_cabang"]
overlap = tier["overlap_heatmap"]
regional = tier["regional"]

# Prioritas = dua tier teratas (berdasarkan urutan tier di Excel)
cps_prio = cps_rows[:2]
mps_prio = mps_rows[:2]
cps_prio_lbl = tier_span_label(cps_prio)
mps_prio_lbl = tier_span_label(mps_prio)

total_kota = sum(num(r["jumlah_kota"]) for r in cps_rows)
kota_prio = sum(num(r["jumlah_kota"]) for r in cps_prio)
hadir_prio = sum(num(r["kota_hadir"]) for r in cps_prio)
total_cabang = sum(num(r["cabang"]) for r in mps_rows)
cabang_mps_prio = sum(num(r["cabang"]) for r in mps_prio)
total_assessment = sum(num(p["total"]) for p in proposal)

# ============================================================
# Hero
# ============================================================
st.markdown(
    f"""
    <div class="bz-hero">
      <div class="bz-eyebrow">OCBC · Biz Lens{esc(periode_text(" · "))}</div>
      <h1 class="bz-title">Potensi kota &amp; cabang untuk ekspansi OCBC</h1>
      <p class="bz-sub">
        Satu pintu untuk melihat {fmt_bulat(total_kota)} kota/kabupaten di Indonesia dan
        {fmt_bulat(total_cabang)} cabang eksisting lewat <b>City Potential Score (CPS)</b>,
        <b>Market Potential Score (MPS)</b>, dan hasil <b>360 Assessment</b>.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Ringkasan nasional
# ============================================================
section_header("Ringkasan nasional", periode_text("Potret OCBC per ", ".") or "Potret OCBC secara nasional.")
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Kota/kabupaten dinilai", fmt_bulat(total_kota),
             f"{fmt_bulat(kota_prio)} di antaranya prioritas ({esc(cps_prio_lbl)})")
with k2:
    kpi_card("Kota prioritas digarap", fmt_bulat(hadir_prio),
             f"dari {fmt_bulat(kota_prio)} kota · cakupan {fmt_pct(ratio(hadir_prio, kota_prio))}")
with k3:
    kpi_card("Kota prioritas belum digarap", fmt_bulat(kota_prio - hadir_prio),
             f"Kota {esc(cps_prio_lbl)} tanpa kehadiran OCBC")
with k4:
    kpi_card("Total cabang OCBC", fmt_bulat(total_cabang),
             f"{fmt_pct(ratio(cabang_mps_prio, total_cabang))} di pasar MPS {esc(mps_prio_lbl)}")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ============================================================
# 360 Assessment
# ============================================================
section_header(
    "360 Assessment — Proposal cabang eksisting" + periode_text(" (", ")"),
    f"Memetakan {fmt_bulat(total_assessment)} cabang terhadap potensi pasar (MPS) dan kehadiran OCBC (CPS).",
)

# Warna & nama kategori diambil dari sheet proposal_cabang
cat_color = {p["kategori_id"]: (p.get("warna") or "#999999") for p in proposal}
cat_name = {p["kategori_id"]: (p.get("kategori") or p["kategori_id"]) for p in proposal}

with st.container(border=True):
    st.markdown(
        '<div class="bz-card-h">Overlap heatmap — MPS × CPS</div>'
        '<div class="bz-card-note">Angka = jumlah cabang. Sel kiri-atas berarti potensi &amp; kehadiran sama-sama tinggi.</div>',
        unsafe_allow_html=True,
    )

    cells = [c for c in overlap if isinstance(c.get("mps_urut"), int) and isinstance(c.get("cps_urut"), int)]
    if not cells:
        st.info("Sheet `overlap_heatmap` masih kosong.")
    else:
        n_rows = max(c["mps_urut"] for c in cells)
        n_cols = max(c["cps_urut"] for c in cells)
        # Label baris/kolom dari kolom mps_label / cps_label di Excel
        mps_lbl = {c["mps_urut"]: c.get("mps_label") for c in cells}
        cps_lbl = {c["cps_urut"]: c.get("cps_label") for c in cells}
        grid_val = {(c["mps_urut"], c["cps_urut"]): c for c in cells}

        grid = [f'<div style="display:grid;grid-template-columns:6rem repeat({n_cols},1fr);gap:6px;margin:0.5rem 0 0.75rem">']
        grid.append("<div></div>")
        for j in range(1, n_cols + 1):
            grid.append(
                '<div style="text-align:center;font-size:0.75rem;color:#8A8A8A;padding:4px 2px;line-height:1.3">'
                f'CPS<br><b style="color:#1A1A1A;font-size:0.82rem">{esc(cps_lbl.get(j, j))}</b></div>'
            )
        for i in range(1, n_rows + 1):
            grid.append(
                '<div style="display:flex;flex-direction:column;justify-content:center;text-align:center;'
                'font-size:0.75rem;color:#8A8A8A;line-height:1.3">'
                f'MPS<br><b style="color:#1A1A1A;font-size:0.82rem">{esc(mps_lbl.get(i, i))}</b></div>'
            )
            for j in range(1, n_cols + 1):
                cell = grid_val.get((i, j))
                if cell is None or cell.get("nilai") is None:
                    grid.append('<div style="background:#F3F2EF;border-radius:6px;min-height:62px"></div>')
                    continue
                kat = cell.get("kategori")
                tip = (f"MPS {mps_lbl.get(i, i)} · CPS {cps_lbl.get(j, j)}: "
                       f"{fmt_bulat(cell['nilai'])} cabang ({cat_name.get(kat, kat or '')})")
                grid.append(
                    f'<div title="{esc(tip)}" style="background:{esc(cat_color.get(kat, "#999999"))};color:white;'
                    'display:flex;align-items:center;justify-content:center;min-height:62px;border-radius:6px;'
                    f'font-size:1.6rem;font-weight:700;cursor:default">{fmt_bulat(cell["nilai"])}</div>'
                )
        grid.append("</div>")
        st.markdown("".join(grid), unsafe_allow_html=True)

        # Legend: jumlah per kategori = total sel heatmap dengan kategori itu
        per_kat = {}
        for c in cells:
            per_kat[c.get("kategori")] = per_kat.get(c.get("kategori"), 0) + num(c.get("nilai"))
        order = [p["kategori_id"] for p in proposal] + [k for k in per_kat if k not in cat_color]
        items = []
        for kid in order:
            if kid not in per_kat:
                continue
            items.append(
                '<span style="display:inline-flex;align-items:center;gap:6px">'
                f'<span style="display:inline-block;width:14px;height:14px;background:{esc(cat_color.get(kid, "#999999"))};border-radius:3px"></span>'
                f'{esc(cat_name.get(kid, kid))} <b>({fmt_bulat(per_kat[kid])})</b></span>'
            )
        st.markdown(
            '<div style="display:flex;flex-wrap:wrap;gap:1.25rem;font-size:0.82rem;color:#333;margin-top:0.25rem">'
            + "".join(items) + "</div>",
            unsafe_allow_html=True,
        )

# Kartu per kategori (jumlahnya mengikuti baris di sheet proposal_cabang)
if proposal:
    per_row = 3
    for start in range(0, len(proposal), per_row):
        chunk = proposal[start:start + per_row]
        cols = st.columns(per_row, gap="medium")
        for col, cat in zip(cols, chunk):
            with col, st.container(border=True):
                color = cat.get("warna") or "#999999"
                st.markdown(
                    f'<div class="bz-cat-head">'
                    f'<div class="bz-cat-eyebrow" style="color:{esc(color)}">{esc(cat.get("deskripsi"))}</div>'
                    f'<h3 class="bz-cat-title">{esc(cat.get("kategori"))}</h3>'
                    f'<div class="bz-cat-total" style="color:{esc(color)}">{fmt_bulat(cat.get("total"))}</div>'
                    f'<div class="bz-cat-cat">cabang</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )
                dist = cat.get("dist_cps") or {}
                if dist:
                    df_dist = pd.DataFrame([{"Tier": t, "Jumlah": v} for t, v in dist.items()])
                    fig = go.Figure(go.Bar(
                        x=df_dist["Tier"], y=df_dist["Jumlah"],
                        marker=dict(color=color),
                        text=df_dist["Jumlah"], textposition="outside",
                        hovertemplate="<b>%{x}</b><br>%{y} cabang<extra></extra>",
                    ))
                    fig.update_layout(
                        height=160, margin=dict(l=0, r=0, t=20, b=0),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(tickfont=dict(size=10), showgrid=False, type="category"),
                        yaxis=dict(visible=False), showlegend=False,
                    )
                    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
                total_close = sum(num(v) for v in (cat.get("close") or {}).values())
                total_review = sum(num(v) for v in (cat.get("review") or {}).values())
                st.markdown(
                    "<div style='display:flex;gap:0.5rem;font-size:0.78rem;margin-top:0.25rem'>"
                    "<div style='flex:1;padding:0.4rem;background:#F8F6F3;border-radius:6px;text-align:center'>"
                    "<div style='color:#8A8A8A'>Close</div>"
                    f"<div style='font-weight:700;font-size:1.1rem'>{fmt_bulat(total_close)}</div></div>"
                    "<div style='flex:1;padding:0.4rem;background:#F8F6F3;border-radius:6px;text-align:center'>"
                    "<div style='color:#8A8A8A'>Review 1Y</div>"
                    f"<div style='font-weight:700;font-size:1.1rem'>{fmt_bulat(total_review)}</div></div>"
                    "</div>",
                    unsafe_allow_html=True,
                )
                if cat.get("catatan"):
                    st.caption(f"* {cat['catatan']}")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ============================================================
# Sebaran regional
# ============================================================
section_header("Sebaran potensi per wilayah", "Rata-rata CPS dan kehadiran OCBC per pulau.")

reg = [r for r in regional if r.get("nama") is not None and isinstance(r.get("cps_rata"), (int, float))]
if not reg:
    st.info("Sheet `regional` masih kosong.")
else:
    df_reg = pd.DataFrame(reg)
    df_reg["jumlah_kota"] = pd.to_numeric(df_reg["jumlah_kota"], errors="coerce").fillna(0)
    df_reg["kota_hadir"] = pd.to_numeric(df_reg["kota_hadir"], errors="coerce").fillna(0)
    df_reg["belum"] = df_reg["jumlah_kota"] - df_reg["kota_hadir"]
    df_reg["cakupan"] = df_reg.apply(lambda r: r["kota_hadir"] / r["jumlah_kota"] if r["jumlah_kota"] else 0, axis=1)

    with st.container(border=True):
        col_m1, col_m2 = st.columns([3, 2], gap="medium")
        with col_m1:
            df_sorted = df_reg.sort_values("cps_rata", ascending=True)
            fig_reg = go.Figure(go.Bar(
                y=df_sorted["nama"], x=df_sorted["cps_rata"], orientation="h",
                marker=dict(color=df_sorted["cps_rata"],
                            colorscale=[[0, OCBC_RED_SOFT], [0.5, OCBC_RED_3], [1, OCBC_RED]],
                            showscale=False),
                text=df_sorted["cps_rata"], textposition="outside",
                customdata=df_sorted[["jumlah_kota", "kota_hadir", "cakupan"]].values,
                hovertemplate=("<b>%{y}</b><br>Rata-rata CPS: %{x}<br>"
                               "%{customdata[0]:,.0f} kota · %{customdata[1]:,.0f} ada OCBC "
                               "(%{customdata[2]:.0%})<extra></extra>"),
            ))
            fig_reg.update_layout(
                height=max(200, 40 * len(df_sorted) + 40), margin=dict(l=10, r=40, t=20, b=10),
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(range=[0, 100], showgrid=True, gridcolor="#F0F0F0",
                           title="Rata-rata CPS", tickfont=dict(size=10)),
                yaxis=dict(tickfont=dict(size=11)),
            )
            st.plotly_chart(fig_reg, use_container_width=True, config={"displayModeBar": False})

        with col_m2:
            # Insight dihitung dari data, bukan ditulis manual
            total_k = df_reg["jumlah_kota"].sum()
            avg_cps = (df_reg["cps_rata"] * df_reg["jumlah_kota"]).sum() / total_k if total_k else df_reg["cps_rata"].mean()
            top = df_reg.loc[df_reg["cps_rata"].idxmax()]
            low = df_reg.loc[df_reg["cps_rata"].idxmin()]
            pool = df_reg[df_reg["cps_rata"] >= avg_cps]
            if pool.empty:
                pool = df_reg
            opp = pool.loc[pool["belum"].idxmax()]

            red = f'style="color:{OCBC_RED}"'
            bullets = [
                f'<b {red}>{esc(top["nama"])}</b> punya rata-rata CPS tertinggi '
                f'(<b>{top["cps_rata"]:g}</b>), dengan cakupan OCBC {fmt_pct(top["cakupan"])} '
                f'({fmt_bulat(top["kota_hadir"])} dari {fmt_bulat(top["jumlah_kota"])} kota).',
                f'<b {red}>{esc(opp["nama"])}</b> punya kota belum digarap terbanyak di antara wilayah '
                f'dengan CPS di atas rata-rata nasional ({avg_cps:.1f}): '
                f'<b>{fmt_bulat(opp["belum"])}</b> kota, CPS {opp["cps_rata"]:g}.',
            ]
            if low["nama"] != top["nama"]:
                bullets.append(
                    f'<b {red}>{esc(low["nama"])}</b> punya rata-rata CPS terendah '
                    f'(<b>{low["cps_rata"]:g}</b>), cakupan OCBC {fmt_pct(low["cakupan"])}.'
                )
            st.markdown(
                '<div class="bz-card-h">Insight</div>'
                '<div style="margin-top:0.5rem;font-size:0.9rem;line-height:1.5">'
                + "<br><br>".join("• " + b for b in bullets) + "</div>",
                unsafe_allow_html=True,
            )

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ============================================================
# Navigasi ke sub-dashboard
# ============================================================
section_header("Pilih dashboard", "Masuk ke profil kota atau cabang untuk analisis detail.")

dims = list(dict.fromkeys(d for k in kota_all.values() for d in (k.get("skor_dimensi") or {})))
mpi_comp = list(dict.fromkeys(c for b in cabang_all.values() for c in (b.get("mpi_components") or {})))

col_1, col_2 = st.columns(2, gap="large")
with col_1, st.container(border=True):
    st.markdown(
        f"""
        <div style="font-size:1.75rem;line-height:1">🏙️</div>
        <h3 style="margin:0.5rem 0 0.25rem;font-weight:600">City Profile</h3>
        <p style="color:#4a4a4a;line-height:1.5;margin:0 0 0.5rem">
          Pindai setiap kota: skor CPI, demografi, pasar perbankan, dan lanskap kompetisi.
        </p>
        <div style="color:#8A8A8A;font-size:0.8rem;margin-bottom:0.5rem">
          {fmt_bulat(len(kota_all))} profil kota tersedia · {fmt_bulat(len(dims))} dimensi penilaian
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Buka City Profile  →", key="go_city", use_container_width=True, type="primary"):
        st.switch_page("city_profile.py")

with col_2, st.container(border=True):
    st.markdown(
        f"""
        <div style="font-size:1.75rem;line-height:1">🏢</div>
        <h3 style="margin:0.5rem 0 0.25rem;font-weight:600">Branch Profile</h3>
        <p style="color:#4a4a4a;line-height:1.5;margin:0 0 0.5rem">
          Pindai setiap cabang: MPI score, tier internal, lingkungan sekitarnya, dan cabang tetangga.
        </p>
        <div style="color:#8A8A8A;font-size:0.8rem;margin-bottom:0.5rem">
          {fmt_bulat(len(cabang_all))} profil cabang tersedia · {fmt_bulat(len(mpi_comp))} komponen MPI
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Buka Branch Profile  →", key="go_branch", use_container_width=True, type="primary"):
        st.switch_page("branch_profile.py")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ============================================================
# Glossary (daftar dimensi, komponen, dan tier diambil dari Excel)
# ============================================================
section_header("Tentang BizLens")

area = info.get("area_layanan")
with st.expander("Apa itu CPS, MPS, dan 360 Assessment?", expanded=False):
    lines = [
        f"- **City Potential Score (CPS)** – skor potensi tiap kota/kabupaten (0–100)"
        + (f" dari {len(dims)} dimensi: {', '.join(dims)}." if dims else "."),
        f"- **Market Potential Score (MPS)** – skor potensi pasar di area layanan tiap cabang"
        + (f" ({area})" if area else "")
        + (f", dari {len(mpi_comp)} komponen: {', '.join(mpi_comp)}." if mpi_comp else "."),
        "- **Internal Score** – skor performa & profitabilitas internal cabang.",
        "- **360 Assessment** – memetakan tiap cabang terhadap kombinasi MPS × CPS untuk "
        "merekomendasikan tindakan (close atau review).",
    ]
    if cps_rows:
        lines.append(f"- Tier CPS: **{tier_range_text(cps_rows)}**.")
    if mps_rows:
        lines.append(f"- Tier MPS: **{tier_range_text(mps_rows)}**.")
    st.markdown("\n".join(lines))

footer()
