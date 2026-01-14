import os
import time
import tempfile
import streamlit as st
from PIL import Image

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    TimeoutException,
    StaleElementReferenceException
)

# ============================================================
# MAIN WRAPPER (FOR unified_app.py )
# ============================================================
def main():

    # --- Page Config ---
    st.set_page_config(page_title="Image Intelligence Analyzer", layout="wide")

    # --- Enhanced UI/UX Styling  ---
    st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #ffffff; }
    .stAlert { border-radius: 10px; }
    div[data-testid="stExpander"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        margin-bottom: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .geo-text {
        font-family: 'Inter', sans-serif;
        line-height: 1.6;
        color: #e0e0e0;
        background: #1c1f26;
        padding: 20px;
        border-radius: 8px;
        border-left: 4px solid #00d4ff;
        white-space: pre-wrap;
    }
    .section-header {
        color: #00d4ff;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ========================================================
    # CORE LOGIC
    # ========================================================
    def run_metadata_analyzer(img_path):
        results_data = {
            "pi7": [],
            "ai_content": "",
            "geospy": [],
            "map_url": None  # ✅ MAP LINK
        }

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 20)

        try:
            # ================= PHASE 1  =================
            driver.get("https://image.pi7.org/photo-metadata-viewer")
            upload_input = wait.until(EC.presence_of_element_located((By.ID, "files")))
            upload_input.send_keys(img_path)
            wait.until(EC.presence_of_element_located((By.ID, "metaeditorx")))
            time.sleep(3)

            target_sections = {
                "PRIMARY IMAGE TAGS": "t_0th",
                "CAMERA & PHOTO DETAILS": "t_Exif",
                "GEOLOCATION INFO (GPS)": "t_GPS"
            }

            extract_js = """
            var sectionId = arguments[0];
            var data = [];
            var container = document.getElementById(sectionId);
            if (container) {
                var labels = container.querySelectorAll('label');
                for (var i = 0; i < labels.length; i++) {
                    var input = labels[i].querySelector('input');
                    if (input && input.value && input.value.trim() !== "") {
                        var labelText = labels[i].innerText.replace(input.value, "").trim();
                        data.push(labelText + ": " + input.value.trim());
                    }
                }
            }
            return data;
            """

            for title, section_id in target_sections.items():
                sec_results = driver.execute_script(extract_js, section_id)
                results_data["pi7"].append({"title": title, "data": sec_results})

            # ======== PHASE 2 — IMAGE CONTENT ANALYSIS==========
            driver.get("https://aiimagechecker.net/imagedetect")
            time.sleep(2)
            driver.find_element(By.CSS_SELECTOR, 'input[type="file"]').send_keys(img_path)

            poll_js = """
            const el = document.querySelector(
                'div.whitespace-pre-wrap.font-mono.text-sm.bg-gray-50.p-4.rounded-lg'
            );
            if (!el) return null;
            return el.innerText.trim().length > 50 ? el.innerText.trim() : null;
            """

            start_time = time.time()
            while time.time() - start_time < 30:
                analysis_text = driver.execute_script(poll_js)
                if analysis_text:
                    results_data["ai_content"] = analysis_text
                    break
                time.sleep(1)

            # ================= PHASE 3 — GEOLOCATION =================
            driver.get("https://aiimagechecker.net/geospy")
            time.sleep(2)
            driver.find_element(By.CSS_SELECTOR, 'input[type="file"]').send_keys(img_path)

            poll_geo_js = """
            const blocks = document.querySelectorAll(
              'section[aria-label="Photo Analysis Tool"] div.grid.grid-cols-1.md\\\\:grid-cols-2.gap-6 > div'
            );

            if (!blocks || blocks.length < 1) return null;

            let output = [];
            blocks.forEach(b => {
                const txt = b.innerText.trim();
                if (txt.length > 20) output.push(txt);
            });

            const mapLink = document.querySelector(
              'section[aria-label="Photo Analysis Tool"] a[href*="google.com/maps"]'
            );

            return {
                blocks: output,
                map: mapLink ? mapLink.href : null
            };
            """

            start_time = time.time()
            while time.time() - start_time < 30:
                geo_data = driver.execute_script(poll_geo_js)
                if geo_data:
                    results_data["geospy"] = geo_data["blocks"]
                    results_data["map_url"] = geo_data["map"]
                    break
                time.sleep(1)

        finally:
            driver.quit()

        return results_data

    # ========================================================
    # STREAMLIT LAYOUT AND INTERACTIONS
    # ========================================================
    st.title("🌐 OSINT Image Forensics")

    col_left, col_right = st.columns([1, 2], gap="large")

    with col_left:
        st.markdown("<div class='section-header'>Source Image</div>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload image for deep analysis", type=["jpg", "jpeg", "png"])

        if uploaded_file:
            st.image(uploaded_file, caption="Target Scan", use_container_width=True)

            if st.button("🚀 Run Intelligence Analysis", use_container_width=True, type="primary"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp:
                    tmp.write(uploaded_file.getvalue())
                    tmp_path = tmp.name

                with st.spinner("Decoding image signatures..."):
                    results = run_metadata_analyzer(tmp_path)
                    st.session_state["results"] = results

                os.remove(tmp_path)

    with col_right:
        st.markdown("<div class='section-header'>Intelligence Reports</div>", unsafe_allow_html=True)

        if "results" in st.session_state:
            res = st.session_state["results"]

            with st.expander("📊 Image Metadata Extraction"):
                for section in res["pi7"]:
                    st.markdown(f"**{section['title']}**")
                    if section["data"]:
                        for line in section["data"]:
                            st.text(line)
                    else:
                        st.caption("No markers found.")

            with st.expander("🧠 AI Visual Description"):
                if res["ai_content"]:
                    st.markdown(f"<div class='geo-text'>{res['ai_content']}</div>", unsafe_allow_html=True)
                else:
                    st.info("Visual content engine returned no text.")

            with st.expander("📍 Geolocation Intelligence", expanded=True):
                if res["geospy"]:
                    for block in res["geospy"]:
                        st.markdown(f"<div class='geo-text'>{block}</div>", unsafe_allow_html=True)
                        st.markdown("<br>", unsafe_allow_html=True)

                    if res["map_url"]:
                        st.markdown(f"[🌍 View on Google Maps]({res['map_url']})")
                else:
                    st.warning("No geolocation data could be inferred.")
        else:
            st.info("System ready. Please upload an image to begin extraction.")


# ============================================================
# STANDALONE SUPPORT
# ============================================================
if __name__ == "__main__":
    main()
