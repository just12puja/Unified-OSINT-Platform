import streamlit as st
import tempfile
import os
import requests
from io import BytesIO
import textwrap

from apify_fetcher import fetch_instagram, fetch_facebook, fetch_linkedin
from normalizer import normalize_post
from graph_builder import build_semantic_knowledge_graph, visualize_semantic_graph

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Semantic OSINT Intelligence Platform",
    layout="wide"
)

st.markdown("## 🧠 Semantic OSINT Intelligence Platform")
st.markdown(
    "Single-target OSINT analysis with confidence-weighted intelligence graph."
)

# ---------------- SIDEBAR ----------------
platform = st.sidebar.selectbox(
    "Select Platform",
    ["Instagram", "Facebook", "LinkedIn"]
)

username = st.sidebar.text_input(
    "Target username / page",
    placeholder="e.g. virat.kohli"
)

run = st.sidebar.button("Run Analysis")

# ---------------- HELPERS ----------------
def load_image_bytes(url):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return BytesIO(r.content)
    except:
        pass
    return None


def short_text(text, width=180):
    return textwrap.shorten(text, width=width, placeholder="...")


# ---------------- EXECUTION ----------------
if run and username:
    st.info("Collecting public intelligence…")

    if platform == "Instagram":
        raw = fetch_instagram(username)
        key = "instagram"

    elif platform == "Facebook":
        raw = fetch_facebook(username)
        key = "facebook"

    else:
        raw = fetch_linkedin(username)
        key = "linkedin"

    if not raw:
        st.warning(
            "No public posts could be retrieved. "
            "For Facebook, only public Pages are accessible."
        )
        st.stop()

    posts = [
        normalize_post(p, key, i)
        for i, p in enumerate(raw[:5], 1)
        if p
    ]

    # ---------------- POSTS (COMPACT CARDS) ----------------
    st.markdown("## 📄 Extracted Posts (Top 5)")

    for i, post in enumerate(posts, 1):
        with st.container(border=True):
            st.markdown(f"**Post {i}**")
            st.caption(post["timestamp"] or "UNKNOWN TIME")

            st.write(short_text(post["text"], 220))

            # Image (compact)
            if post["image_url"]:
                img_bytes = load_image_bytes(post["image_url"])
                if img_bytes:
                    st.image(img_bytes, width=420)
                else:
                    st.caption("Image present but blocked by CDN.")

            # Video info (no fake playback)
            if post["video_url"]:
                st.video(post["video_url"])
            elif post["has_video"]:
                st.caption("🎥 Video present (direct playback restricted)")

    # ---------------- GRAPH (RELIABLE RENDERING) ----------------
    st.markdown("## 🕸️ Intelligence Knowledge Graph")

    graph = build_semantic_knowledge_graph(posts, username, key)

    with tempfile.TemporaryDirectory() as tmpdir:
        graph_path = os.path.join(tmpdir, "graph.png")
        visualize_semantic_graph(graph, graph_path)

        # ✅ CORRECT: render directly, NOT via iframe src
        st.image(
            graph_path,
            use_container_width=True,
            caption="Confidence-Weighted Semantic OSINT Graph"
        )

    st.success("Intelligence analysis completed.")
