"""City Profile – indikator per kota."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from styling import section_header, kpi_card, tier_badge, OCBC_RED, OCBC_RED_2, OCBC_RED_3
from bizlens_data import (
    load_kota, load_tier, tier_threshold, sorted_tiers, footer,
    fmt_bulat, fmt_pct, fmt_rp_t, fmt_rp_jt, fmt_jt,
)


def div(a, b):
    """Pembagian aman: None kalau datanya kosong / nol."""
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)) or b == 0:
        return None
    return a / b


def times(x) -> str:
    return "–" if x is None else f"{x:.1f}×"

# ============================================================
# Breadcrumb + city picker
# ============================================================
col_bc, col_pick = st.columns([3, 2])
with col_bc:
    if st.button("← Kembali ke BizLens", key="back"):
        st.switch_page("home.py")
with col_pick:
    kota_all = load_kota()
    kota_key = st.selectbox(
        "Pilih kota",
        options=list(kota_all.keys()),
        format_func=lambda k: kota_all[k].get("nama") or k,
        label_visibility="collapsed",
    )

k = kota_all[kota_key]

# ============================================================
# Hero
# ============================================================
cpi_tier_txt = " ".join(str(x) for x in [k.get("cpi_tier"), f"({k['cpi_tier_batas']})" if k.get("cpi_tier_batas") else None] if x)
st.markdown(
    f"""
    <div class="bz-hero" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1.5rem">
      <div style="flex:1 1 22rem;min-width:0">
        <div class="bz-eyebrow">City Profile{" · " + str(k["provinsi"]) if k.get("provinsi") else ""}</div>
        <h1 class="bz-title">{k.get("nama") or kota_key}</h1>
        <p class="bz-sub">{k.get("ringkasan") or ""}</p>
      </div>
      <div style="flex:0 0 auto;background:#fff;border:1px solid #E6E4E0;border-radius:12px;padding:1rem 1.5rem;text-align:center">
        <div style="font-size:0.78rem;color:#8A8A8A;font-weight:500">Skor CPI</div>
        <div style="font-size:2.6rem;font-weight:700;color:{OCBC_RED};line-height:1">{fmt_bulat(k.get("cpi_score"))}<span style="font-size:1rem;color:#8A8A8A;font-weight:400">/100</span></div>
        <div style="margin-top:0.5rem">{tier_badge(cpi_tier_txt) if cpi_tier_txt else ""}</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Indikator utama
# ============================================================
section_header("Indikator utama", "Hijau = di atas rata-rata nasional · Merah = di bawahnya.")

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    ratio_pop = div(k["populasi"], k["populasi_avg_nasional"])
    kpi_card("Populasi", fmt_jt(k["populasi"]),
             f"{times(ratio_pop)} rata-rata · peringkat #{fmt_bulat(k['populasi_peringkat'])}",
             "" if ratio_pop is None else ("up" if ratio_pop >= 1 else "down"))
with k2:
    kpi_card("PDRB (GRDP)", fmt_rp_t(k["pdrb_t"]),
             f"Tumbuh {fmt_pct(k['pdrb_tumbuh'], 1)}/thn (nasional {fmt_pct(k['pdrb_tumbuh_nasional'], 1)})",
             "" if div(k["pdrb_tumbuh"], 1) is None or div(k["pdrb_tumbuh_nasional"], 1) is None
             else ("up" if k["pdrb_tumbuh"] >= k["pdrb_tumbuh_nasional"] else "down"))
with k3:
    ratio = div(k["pdrb_kapita_jt"], k["pdrb_kapita_nasional_jt"])
    kpi_card("PDRB per kapita", fmt_rp_jt(k["pdrb_kapita_jt"]),
             f"{times(ratio)} rata-rata · peringkat #{fmt_bulat(k['pdrb_kapita_peringkat'])}",
             "" if ratio is None else ("up" if ratio >= 1 else "down"))
with k4:
    kpi_card("Usia produktif", fmt_pct(k["usia_produktif"]),
             f"vs nasional {fmt_pct(k['usia_produktif_nasional'])} · peringkat #{fmt_bulat(k['usia_produktif_peringkat'])}",
             "" if div(k["usia_produktif"], 1) is None or div(k["usia_produktif_nasional"], 1) is None
             else ("up" if k["usia_produktif"] >= k["usia_produktif_nasional"] else "down"))
with k5:
    pangsa = div(k["cabang_ocbc"], sum(v for v in k["cabang_bank"].values() if isinstance(v, (int, float))))
    kpi_card("Cabang OCBC", fmt_bulat(k["cabang_ocbc"]),
             f"{fmt_pct(pangsa, 1)} dari seluruh cabang bank")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ============================================================
# Skor dimensi
# ============================================================
skor = {d: v for d, v in k["skor_dimensi"].items() if isinstance(v, (int, float))}
cps_tiers = sorted_tiers(load_tier()["tier_distribution_cps"])
acuan = tier_threshold(cps_tiers)            # batas tier teratas dari sheet tier_cps
acuan_tier = cps_tiers[0]["tier"] if cps_tiers else None
acuan_txt = f" Acuan {acuan_tier} = {acuan:g}." if acuan is not None else ""

section_header("Skor kota per dimensi", f"{len(skor)} dimensi penilaian, skala 0–100.{acuan_txt}")
if not skor:
    st.info("Belum ada skor dimensi untuk kota ini di sheet `city_dims`.")
    st.stop()

dims = list(skor.keys())
vals = list(skor.values())

col_r, col_b = st.columns(2, gap="medium")

with col_r:
    with st.container(border=True):
        st.markdown(
            '<div class="bz-card-h">🎯 Peta kekuatan</div>'
            '<div class="bz-card-note">Makin luas bentuknya, makin seimbang kota ini</div>',
            unsafe_allow_html=True,
        )
        fig = go.Figure()
        if acuan is not None:
            fig.add_trace(go.Scatterpolar(
                r=[acuan] * (len(dims) + 1),
                theta=dims + [dims[0]],
                line=dict(color="#AAA", width=1, dash="dash"),
                fill=None, showlegend=False, hoverinfo="skip",
            ))
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]],
            theta=dims + [dims[0]],
            line=dict(color=OCBC_RED, width=2.5),
            fill="toself",
            fillcolor="rgba(215,38,46,0.15)",
            hovertemplate="<b>%{theta}</b><br>Skor: %{r:.1f}<extra></extra>",
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], tickfont=dict(size=10, color="#8A8A8A"), gridcolor="#E6E4E0"),
                angularaxis=dict(tickfont=dict(size=11, color="#1A1A1A"), gridcolor="#E6E4E0"),
                bgcolor="rgba(0,0,0,0)",
            ),
            showlegend=False, margin=dict(l=40, r=40, t=20, b=20),
            height=300, paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

with col_b:
    with st.container(border=True):
        st.markdown(
            '<div class="bz-card-h">📊 Urutan skor</div>'
            '<div class="bz-card-note">Dari tertinggi ke terendah'
            + (f' · abu-abu = di bawah acuan {acuan:g}' if acuan is not None else '') + '</div>',
            unsafe_allow_html=True,
        )
        sorted_dims = sorted(skor.items(), key=lambda x: x[1], reverse=True)
        bar_colors = [OCBC_RED if acuan is None or v >= acuan else "#C9C9C9" for _, v in sorted_dims]
        fig2 = go.Figure(go.Bar(
            y=[d for d, _ in sorted_dims],
            x=[v for _, v in sorted_dims],
            orientation="h",
            marker=dict(color=bar_colors),
            text=[f"{v:.1f}" for _, v in sorted_dims],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>Skor: %{x:.1f}<extra></extra>",
        ))
        if acuan is not None:
            fig2.add_vline(x=acuan, line=dict(color="#8A8A8A", width=1, dash="dash"))
        fig2.update_layout(
            margin=dict(l=10, r=50, t=20, b=20), height=300,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(range=[0, 110], showgrid=True, gridcolor="#F0F0F0", tickfont=dict(size=10)),
            yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ============================================================
# Pasar perbankan
# ============================================================
section_header("Potensi pasar & investasi", "Ukuran pasar perbankan di kota ini.")

c1, c2, c3 = st.columns(3, gap="medium")

with c1:
    with st.container(border=True):
        st.markdown(
            '<div class="bz-card-h">👥 Basis nasabah</div>'
            '<div class="bz-card-note">Penetrasi perbankan dan jumlah pelaku usaha</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p class="bz-big-num">{fmt_pct(k["penetrasi_bank"])}'
            f'<span style="font-size:0.78rem;color:#8A8A8A;margin-left:0.5rem;font-weight:400">penetrasi perbankan</span></p>',
            unsafe_allow_html=True,
        )
        st.progress(k["penetrasi_bank"])
        st.caption(f"{fmt_pct(1 - k['penetrasi_bank'])} belum terlayani bank: ruang akuisisi nasabah baru")
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(
                f'<div class="bz-mini"><div class="bz-mini-v">{k["jumlah_umkm"] / 1000:.1f} rb</div>'
                f'<div class="bz-mini-l">Usaha UMKM/EmB</div></div>',
                unsafe_allow_html=True,
            )
        with m2:
            st.markdown(
                f'<div class="bz-mini"><div class="bz-mini-v">{fmt_bulat(k["jumlah_korporasi"])}</div>'
                f'<div class="bz-mini-l">Segmen korporasi</div></div>',
                unsafe_allow_html=True,
            )

with c2:
    with st.container(border=True):
        st.markdown(
            '<div class="bz-card-h">💰 Dana Pihak Ketiga (DPK)</div>'
            '<div class="bz-card-note">Total simpanan masyarakat di bank</div>',
            unsafe_allow_html=True,
        )
        lain = (k["dpk_t"] - (k["tabungan_t"] or 0) - (k["giro_t"] or 0)) if isinstance(k["dpk_t"], (int, float)) else None
        st.markdown(
            f'<p class="bz-big-num">{fmt_rp_t(k["dpk_t"])}</p>',
            unsafe_allow_html=True,
        )
        fig_dpk = go.Figure()
        colors_dpk = [OCBC_RED, OCBC_RED_2, OCBC_RED_3]
        for i, (lab, val) in enumerate([("Giro", k["giro_t"]), ("Deposito & lainnya", lain), ("Tabungan", k["tabungan_t"])]):
            if not isinstance(val, (int, float)):
                continue
            porsi = div(val, k["dpk_t"]) or 0
            fig_dpk.add_trace(go.Bar(
                x=[val], y=["DPK"], orientation="h",
                marker=dict(color=colors_dpk[i]),
                text=f"{lab}<br>Rp{val:.0f} T · {porsi * 100:.0f}%",
                textposition="inside",
                insidetextfont=dict(color="white", size=11),
                hovertemplate=f"<b>{lab}</b><br>Rp{val:.0f} T ({porsi * 100:.1f}%)<extra></extra>",
            ))
        fig_dpk.update_layout(
            barmode="stack", height=100, showlegend=False,
            margin=dict(l=0, r=0, t=10, b=10),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_dpk, use_container_width=True, config={"displayModeBar": False})
        st.caption("Deposito & lainnya = DPK − tabungan − giro")

with c3:
    with st.container(border=True):
        st.markdown(
            '<div class="bz-card-h">💳 Kredit</div>'
            '<div class="bz-card-note">Total penyaluran kredit di kota</div>',
            unsafe_allow_html=True,
        )
        ldr = div(k["kredit_t"], k["dpk_t"])
        st.markdown(
            f'<p class="bz-big-num">{fmt_rp_t(k["kredit_t"])}'
            f'<span class="bz-chip">Kredit/DPK <b>{fmt_pct(ldr)}</b></span></p>',
            unsafe_allow_html=True,
        )
        fig_kr = go.Figure()
        colors_kr = [OCBC_RED, OCBC_RED_2]
        for i, (lab, val) in enumerate([("Kredit UMKM", k["kredit_umkm_t"]), ("Kredit konsumer", k["kredit_konsumer_t"])]):
            if not isinstance(val, (int, float)):
                continue
            porsi = div(val, k["kredit_t"]) or 0
            fig_kr.add_trace(go.Bar(
                x=[val], y=["Kredit"], orientation="h",
                marker=dict(color=colors_kr[i]),
                text=f"{lab}<br>Rp{val:.0f} T · {porsi * 100:.0f}%",
                textposition="inside",
                insidetextfont=dict(color="white", size=11),
                hovertemplate=f"<b>{lab}</b><br>Rp{val:.0f} T ({porsi * 100:.1f}%)<extra></extra>",
            ))
        fig_kr.update_layout(
            barmode="stack", height=100, showlegend=False,
            margin=dict(l=0, r=0, t=10, b=10),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_kr, use_container_width=True, config={"displayModeBar": False})
        st.caption("Kredit/DPK < 100% = dana belum banyak tersalurkan")

# ============================================================
# Kompetisi
# ============================================================
section_header("Lanskap kompetisi", "Jumlah cabang bank yang beroperasi di kota ini.")

bank_groups = {g: v for g, v in k["cabang_bank"].items() if isinstance(v, (int, float))}
total_cabang_bank = sum(bank_groups.values())
pangsa_ocbc_all = div(k["cabang_ocbc"], total_cabang_bank)
# Kelompok bank swasta dicari dari nama kelompok yang mengandung kata "swasta"
swasta = sum(v for g, v in bank_groups.items() if "swasta" in str(g).lower())
pangsa_ocbc_swasta = div(k["cabang_ocbc"], swasta)

ck1, ck2 = st.columns([3, 2], gap="medium")
with ck1:
    with st.container(border=True):
        st.markdown(
            f'<div class="bz-card-h">🏦 Komposisi cabang bank</div>'
            f'<p class="bz-big-num">{fmt_bulat(total_cabang_bank)}'
            f'<span style="font-size:0.8rem;color:#8A8A8A;margin-left:0.5rem;font-weight:400">total cabang bank</span></p>',
            unsafe_allow_html=True,
        )
        fig_kp = go.Figure()
        colors_kp = [OCBC_RED, OCBC_RED_2, OCBC_RED_3, "#C9C9C9", "#8A8A8A"]
        for i, (lab, val) in enumerate(bank_groups.items()):
            porsi = div(val, total_cabang_bank) or 0
            fig_kp.add_trace(go.Bar(
                x=[val], y=["Cabang"], orientation="h",
                marker=dict(color=colors_kp[i % len(colors_kp)]),
                text=f"{lab}<br>{val} · {porsi * 100:.0f}%",
                textposition="inside",
                insidetextfont=dict(color="white", size=11),
                hovertemplate=f"<b>{lab}</b><br>{val} cabang ({porsi * 100:.1f}%)<extra></extra>",
            ))
        fig_kp.update_layout(
            barmode="stack", height=100, showlegend=False,
            margin=dict(l=0, r=0, t=10, b=10),
            xaxis=dict(visible=False), yaxis=dict(visible=False),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_kp, use_container_width=True, config={"displayModeBar": False})

with ck2:
    with st.container(border=True):
        st.markdown(
            f'<div class="bz-card-h" style="color:{OCBC_RED}">🎯 Posisi OCBC</div>'
            f'<p class="bz-big-num red" style="margin-top:0.3rem">{fmt_bulat(k["cabang_ocbc"])} '
            f'<span style="font-size:0.78rem;color:#8A8A8A;font-weight:400">cabang</span></p>'
            f'<div style="font-size:0.9rem;line-height:1.5;color:#333">'
            f'Setara <b>{fmt_pct(pangsa_ocbc_all, 1)}</b> dari seluruh cabang bank di kota'
            + (f',<br>atau <b>{fmt_pct(pangsa_ocbc_swasta, 1)}</b> dari cabang bank swasta.'
               if pangsa_ocbc_swasta is not None else '.')
            + '</div>',
            unsafe_allow_html=True,
        )

# ============================================================
# Infrastruktur
# ============================================================
section_header("Infrastruktur")
inf1, inf2 = st.columns(2)
with inf1:
    with st.container(border=True):
        st.markdown(
            f'<div class="bz-card-h">🛣️ Jalan tol</div>'
            f'<div style="margin-top:0.5rem">{k["jalan_tol"]}</div>',
            unsafe_allow_html=True,
        )
with inf2:
    with st.container(border=True):
        st.markdown(
            f'<div class="bz-card-h">✈️ Bandara</div>'
            f'<div style="margin-top:0.5rem">{k["bandara"]}</div>',
            unsafe_allow_html=True,
        )

footer()
