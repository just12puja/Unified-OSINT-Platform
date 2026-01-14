# ============================
# IMPORT SCOPE FIX (REQUIRED)
# ============================
import sys
import os

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# ============================
# ORIGINAL IMPORTS (UNCHANGED)
# ============================
import streamlit as st
import tempfile
import requests
from io import BytesIO
import streamlit.components.v1 as components

from apify_fetcher import fetch_instagram, fetch_facebook
from normalizer import normalize_post
from graph_builder import build_semantic_knowledge_graph
from pyvis_renderer import render_graph_pyvis


# ============================================================
# MAIN WRAPPER (REQUIRED FOR UNIFIED APP)
# ============================================================
def main():
    # ============================
    # STREAMLIT PAGE CONFIG
    # ============================
    st.set_page_config(
        page_title="Semantic OSINT Intelligence Platform",
        layout="wide"
    )

    st.markdown("## 🧠 Semantic OSINT Intelligence Platform")
    st.markdown("Single-target OSINT analysis with confidence-weighted intelligence graph.")

    # ============================
    # SIDEBAR INPUTS
    # ============================
    platform = st.sidebar.selectbox(
        "Select Platform",
        ["Instagram", "Facebook"]
    )

    username = st.sidebar.text_input(
        "Target username / page",
        placeholder="e.g. carryminati"
    )

    run = st.sidebar.button("Run Analysis")

    # ============================
    # HELPER FUNCTION
    # ============================
    def load_image_bytes(url):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                return BytesIO(r.content)
        except Exception:
            pass
        return None

    # ============================
    # MAIN EXECUTION
    # ============================
    if run and username:
        st.info("Collecting public intelligence…")

        if platform == "Instagram":
            raw = fetch_instagram(username)
            key = "instagram"
        else:
            raw = fetch_facebook(username)
            key = "facebook"

        if not raw:
            st.warning("No public posts could be retrieved.")
            st.stop()

        posts = [
            normalize_post(p, key, i)
            for i, p in enumerate(raw[:7], 1)
            if p
        ]

        # ============================
        # POSTS DISPLAY
        # ============================
        st.markdown("## 📸 Captured Posts")

        cols = st.columns(3)
        for idx, post in enumerate(posts):
            with cols[idx % 3]:
                raw_post = raw[idx] if idx < len(raw) else {}
                shortcode = raw_post.get("shortCode")

                if shortcode and platform == "Instagram":
                    components.html(
                        f"""
                        <iframe
                            src="https://www.instagram.com/p/{shortcode}/embed"
                            width="320"
                            height="420"
                            frameborder="0"
                            scrolling="no"
                            allowtransparency="true">
                        </iframe>
                        """,
                        height=450,
                    )

                elif post.get("image_url"):
                    img = load_image_bytes(post["image_url"])
                    if img:
                        st.image(img, use_container_width=True)
                    else:
                        st.warning("Media unavailable")

                if post.get("text"):
                    st.caption(post["text"][:150])

        # ============================
        # GRAPH GENERATION
        # ============================
        st.markdown("## 🕸️ Intelligence Knowledge Graph")

        graph = build_semantic_knowledge_graph(posts, username, key)

        with tempfile.TemporaryDirectory() as tmpdir:
            html_path = os.path.join(tmpdir, "graph.html")
            render_graph_pyvis(graph, html_path)

            components.html(
                open(html_path, "r", encoding="utf-8").read(),
                height=900,
                scrolling=True
            )

        st.success("Intelligence analysis completed.")


# ============================================================
# ALLOW STANDALONE EXECUTION 
# ============================================================
if __name__ == "__main__":
    main()
