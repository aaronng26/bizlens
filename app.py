"""BizLens – OCBC entry point (flat structure).

Run with:  streamlit run app.py
"""
import sys
from pathlib import Path

# Pastikan folder app ini yang dipakai untuk import (bukan folder lain)
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from styling import inject_css

st.set_page_config(
    page_title="BizLens – OCBC",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()

# ---- Navigation ----------------------------------------------------
# Each page file sits next to this one at the project root.
home = st.Page("home.py", title="BizLens", icon="🏦", default=True)
city = st.Page("city_profile.py", title="City Profile", icon="🏙️")
branch = st.Page("branch_profile.py", title="Branch Profile", icon="🏢")

pg = st.navigation([home, city, branch])
pg.run()
