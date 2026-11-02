"""Branch Profile – MPI, internal, dan cabang tetangga."""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from styling import section_header, kpi_card, tier_badge, OCBC_RED, OCBC_RED_2, OCBC_RED_3
from bizlens_data import load_cabang, load_tier, tier_threshold, sorted_tiers, footer, fmt_bulat

# ============================================================
# Breadcrumb + branch picker
# ============================================================
col_bc, col_pick = st.columns([3, 2])
with col_bc:
    if st.button("← Kembali ke BizLens", key="back"):
        st.switch_page("home.py")
with col_pick:
    cab_all = load_cabang()
    cab_key = st.selectbox(
        "Pilih cabang",
        options=list(cab_all.keys()),
        format_func=lambda k: cab_all[k].get("nama") or k,
        label_visibility="collapsed",
    )

b = cab_all[cab_key]

# ============================================================
# Hero
# ============================================================
st.markdown(
    f"""
    <div class="bz-hero">
      <div class="bz-eyebrow">Branch Profile · {b.get("kota") or "–"}</div>
      <h1 class="bz-title">{b["nama"]}</h1>
      <div style="margin-top:0.5rem">
        {tier_badge("MPI " + str(b["mpi_tier"])) if b.get("mpi_tier") else ""}
        {tier_badge("Internal " + str(b["internal_tier"])) if b.get("internal_tier") else ""}
        {tier_badge("Overlap " + str(b["overlap_tier"])) if b.get("overlap_tier") else ""}
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# Skor ringkasan
# ============================================================
section_header("Skor cabang", "Tiga skor utama yang menilai cabang dari sisi luar dan dalam.")

sc1, sc2, sc3 = st.columns(3)
with sc1:
    kpi_card("MPI Tier Score", fmt_bulat(b.get("mpi_score")), f"{b.get('mpi_tier') or '–'} · Potensi pasar area layanan")
with sc2:
    kpi_card("Internal Tier Score", fmt_bulat(b.get("internal_score")), f"{b.get('internal_tier') or '–'} · Performa internal cabang")
with sc3:
    kpi_card("Overlap Heatmap", fmt_bulat(b.get("overlap_score")), f"{b.get('overlap_tier') or '–'} · Posisi vs cabang tetangga")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ============================================================
# MPI radar + Internal + Nearest
# ============================================================
section_header("MPI Detail vs Internal Component",
               "Kiri: potensi pasar di sekitar cabang. Kanan: performa internal cabang.")

# Acuan garis putus = batas tier MPS teratas dari sheet tier_mps
mps_tiers = sorted_tiers(load_tier()["tier_distribution_mps"])
acuan = tier_threshold(mps_tiers)
acuan_tier = mps_tiers[0]["tier"] if mps_tiers else None
mpi = {c: v for c, v in b["mpi_components"].items() if isinstance(v, (int, float))}

col_r, col_i, col_n = st.columns([2, 1.5, 1.5], gap="medium")

with col_r:
    with st.container(border=True):
        st.markdown(
            '<div class="bz-card-h">🎯 MPI Detail Component</div>'
            f'<div class="bz-card-note">{len(mpi)} komponen pembentuk MPI, skala 0–100'
            + (f' · garis putus = acuan {acuan_tier} ({acuan:g})' if acuan is not None else '')
            + '</div>',
            unsafe_allow_html=True,
        )
        if not mpi:
            st.info("Belum ada komponen MPI untuk cabang ini di sheet `branch_mpi`.")
        else:
            dims = list(mpi.keys())
            vals = list(mpi.values())
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
                showlegend=False, margin=dict(l=50, r=50, t=20, b=20),
                height=280, paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

            cols = st.columns(len(dims))
            for i, (dim, val) in enumerate(mpi.items()):
                with cols[i]:
                    st.markdown(
                        f'<div style="text-align:center;padding:0.25rem 0">'
                        f'<div style="font-size:0.72rem;color:#8A8A8A">{dim}</div>'
                        f'<div style="font-weight:600;font-variant-numeric:tabular-nums">{val:.1f}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

with col_i:
    with st.container(border=True):
        st.markdown(
            '<div class="bz-card-h">🏆 Internal Component</div>'
            '<div class="bz-card-note">Tier internal per komponen</div>',
            unsafe_allow_html=True,
        )
        rows_html = ""
        for lab, val in b["internal_components"].items():
            rows_html += (
                f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.4rem 0;border-bottom:1px solid #F0F0F0">'
                f'<div style="font-size:0.85rem">{lab}</div><div>{tier_badge(val)}</div></div>'
            )
        st.markdown(rows_html, unsafe_allow_html=True)

with col_n:
    with st.container(border=True):
        st.markdown(
            '<div class="bz-card-h">🏛️ Nearest Branch</div>'
            f'<div style="color:{OCBC_RED};font-weight:600;margin:0.25rem 0 0.5rem">{b["nearest_branch"]["nama"]}</div>',
            unsafe_allow_html=True,
        )
        rows_html = ""
        for lab, val in b["nearest_branch"].items():
            if lab == "nama":
                continue
            rows_html += (
                f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.4rem 0;border-bottom:1px solid #F0F0F0">'
                f'<div style="font-size:0.85rem">{lab}</div><div>{tier_badge(val)}</div></div>'
            )
        st.markdown(rows_html, unsafe_allow_html=True)

# ============================================================
# Konteks lingkungan sekitar
# ============================================================
section_header("Konteks lingkungan sekitar", "Jumlah titik per kategori dalam area layanan cabang.")


def context_card(title: str, icon: str, data: dict, color: str):
    """Render a context card with a horizontal bar list inside st.container."""
    with st.container(border=True):
        st.markdown(f'<div class="bz-card-h">{icon} {title}</div>', unsafe_allow_html=True)
        df = pd.DataFrame([{"Kategori": k, "Jumlah": v} for k, v in data.items()])
        df = df.sort_values("Jumlah", ascending=True)
        fig = go.Figure(go.Bar(
            y=df["Kategori"], x=df["Jumlah"],
            orientation="h",
            marker=dict(color=color),
            text=df["Jumlah"].map(fmt_bulat),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>%{x}<extra></extra>",
        ))
        fig.update_layout(
            margin=dict(l=10, r=40, t=10, b=10),
            height=max(140, 32 * len(df) + 60),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(tickfont=dict(size=11)),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


cx1, cx2 = st.columns(2, gap="medium")
with cx1:
    context_card("Commercial Density", "🏬", b["commercial_density"], OCBC_RED)
with cx2:
    context_card("Competition Landscape", "⚔️", b["competition"], OCBC_RED_2)

cx3, cx4 = st.columns(2, gap="medium")
with cx3:
    context_card("Demographic", "👥", b["demographic"], OCBC_RED_3)
with cx4:
    context_card("Economic Hub", "🏭", b["economic_hub"], OCBC_RED)

# ============================================================
# Overlap heatmap
# ============================================================
section_header("Overlap Heatmap Summary", "Jumlah cabang OCBC terdekat berdasarkan jarak dan tipe.")

df_overlap = pd.DataFrame(b["overlap_summary"])
df_overlap = df_overlap.rename(columns={
    "type": "Tipe", "r_2km": "<2 km", "r_2_5km": "2–5 km", "r_5_10km": "5–10 km",
})
cats = df_overlap["Tipe"].tolist()
dists = ["<2 km", "2–5 km", "5–10 km"]
z = df_overlap[dists].values
text = [[fmt_bulat(v) for v in row] for row in z]

col_h, col_t = st.columns([2, 1], gap="medium")
with col_h:
    with st.container(border=True):
        st.markdown('<div class="bz-card-h">Jumlah cabang per jarak × tipe</div>', unsafe_allow_html=True)
        fig_h = go.Figure(go.Heatmap(
            z=z, x=dists, y=cats, text=text, texttemplate="%{text}",
            colorscale=[[0, "#FBECED"], [1, OCBC_RED]],
            showscale=False,
            hovertemplate="<b>%{y}</b> · %{x}<br>%{z} cabang<extra></extra>",
            textfont=dict(size=16, color="#1A1A1A"),
            xgap=4, ygap=4,
        ))
        fig_h.update_layout(
            height=220, margin=dict(l=10, r=10, t=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
            xaxis=dict(side="top", tickfont=dict(size=11)),
        )
        st.plotly_chart(fig_h, use_container_width=True, config={"displayModeBar": False})

with col_t:
    with st.container(border=True):
        st.markdown('<div class="bz-card-h">Total per jarak</div>', unsafe_allow_html=True)
        totals = {d: int(df_overlap[d].sum()) for d in dists}
        total_all = sum(totals.values())
        for d, v in totals.items():
            pct = v / max(1, total_all)
            st.markdown(
                f'<div style="margin:0.5rem 0">'
                f'<div style="display:flex;justify-content:space-between">'
                f'<span>{d}</span><b>{v} cabang</b></div>'
                f'<div style="height:6px;background:#F0F0F0;border-radius:3px;margin-top:4px;overflow:hidden">'
                f'<div style="height:100%;width:{pct * 100}%;background:{OCBC_RED}"></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

# ============================================================
# Overlap heatmap detail
# ============================================================
section_header("Overlap Heatmap Detail",
               "Daftar cabang tetangga lengkap dengan performa dan skor MPI.")

tab1, tab2 = st.tabs([f"Dalam 2 km ({len(b['neighbors_lt_2km'])})", f"2–5 km ({len(b['neighbors_2_5km'])})"])
with tab1:
    if b["neighbors_lt_2km"]:
        df1 = pd.DataFrame(b["neighbors_lt_2km"])
        df1 = df1.rename(columns={
            "nama": "Nama cabang", "type": "Tipe",
            "radius": "Radius (km)", "performance": "Performance", "mpi": "MPI",
        })
        st.dataframe(df1, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada cabang OCBC lain dalam radius 2 km.")

with tab2:
    if b["neighbors_2_5km"]:
        df2 = pd.DataFrame(b["neighbors_2_5km"])
        df2 = df2.rename(columns={
            "nama": "Nama cabang", "type": "Tipe",
            "radius": "Radius (km)", "performance": "Performance", "mpi": "MPI",
        })
        st.dataframe(df2, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada cabang OCBC lain dalam radius 2–5 km.")

footer()
