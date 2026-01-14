import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path registration 
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "image_checker"))
sys.path.insert(0, os.path.join(BASE_DIR, "social_intelligence"))
sys.path.insert(0, os.path.join(BASE_DIR, "Reverse_OSINT"))

import streamlit as st

from social_intelligence.streamlit_app import main as social_main
from image_checker.app import main as image_main
from Reverse_OSINT.app import main as reverse_osint_main

# --------------------------------------------------
# Unified Layout
# --------------------------------------------------
st.set_page_config(
    page_title="Unified OSINT Platform",
    layout="wide"
)

st.title("Unified OSINT Intelligence Platform")

tab1, tab2, tab3 = st.tabs([
    "🔍 Social Intelligence",
    "🖼️ Image Intelligence",
    "🕵️ Reverse OSINT"
])

with tab1:
    social_main()

with tab2:
    image_main()

with tab3:
    reverse_osint_main()
