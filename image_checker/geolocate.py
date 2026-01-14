import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException, TimeoutException

def run_metadata_analyzer():
    # ------------------------------------------------------------
    # INPUT
    # ------------------------------------------------------------
    img_path = input("Enter the full path to your image: ").strip().replace('"', '').replace("'", "")

    if not os.path.exists(img_path):
        print(f"Error: File not found at {img_path}")
        return

    # ------------------------------------------------------------
    # SELENIUM CONFIG
    # ------------------------------------------------------------
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 12)

    try:
        # ============================================================
        #                              PHASE 1 
        # ============================================================
        driver.get("https://image.pi7.org/photo-metadata-viewer")

        upload_input = wait.until(EC.presence_of_element_located((By.ID, "files")))
        try:
            upload_input.send_keys(img_path)
        except UnexpectedAlertPresentException:
            alert = driver.switch_to.alert
            print(f"Upload Error: {alert.text}")
            alert.accept()
            return

        wait.until(EC.presence_of_element_located((By.ID, "metaeditorx")))
        time.sleep(2)

        print("\n" + "=" * 60)
        print("IMAGE METADATA ANALYSIS")
        print("=" * 60)

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

        metadata_found = False

        for title, section_id in target_sections.items():
            print(f"\n[{title}]")
            results = driver.execute_script(extract_js, section_id)
            if results:
                metadata_found = True
                for line in results:
                    print(line)
            else:
                print("No data found.")

        if not metadata_found:
            print("\nMetadata not found in image.")

        # ============================================================
        #                             PHASE 2
        # ============================================================
        print("\n" + "=" * 60)
        print("IMAGE CONTENT ANALYSIS")
        print("=" * 60)

        driver.get("https://aiimagechecker.net/imagedetect")

        upload_js = """
        const input = document.querySelector('input[type="file"]');
        if (!input) return null;
        input.value = null;
        return input;
        """

        file_input = WebDriverWait(driver, 15).until(
            lambda d: d.execute_script(upload_js)
        )
        file_input.send_keys(img_path)

        poll_js = """
        const el = document.querySelector(
          'div.whitespace-pre-wrap.font-mono.text-sm.bg-gray-50.p-4.rounded-lg'
        );
        if (!el) return null;
        const text = el.innerText.trim();
        return text.length > 80 ? text : null;
        """

        analysis_text = None
        start_time = time.time()

        while time.time() - start_time < 30:
            analysis_text = driver.execute_script(poll_js)
            if analysis_text:
                break
            time.sleep(0.4)

        if analysis_text:
            print(analysis_text)
        else:
            print("AI image content analysis not available.")

        # ============================================================
        #                            PHASE 3
        # ============================================================
        print("\n" + "=" * 60)
        print("IMAGE GEOLOCATION ANALYSIS")
        print("=" * 60)

        driver.get("https://aiimagechecker.net/geospy")

        # --- Upload image (hidden input)
        upload_geo_js = """
        const input = document.querySelector('input[type="file"]');
        if (!input) return null;
        input.value = null;
        return input;
        """

        geo_input = WebDriverWait(driver, 15).until(
            lambda d: d.execute_script(upload_geo_js)
        )
        geo_input.send_keys(img_path)

        # --- Poll all result blocks (location cards + explanation)
        poll_geo_js = """
        const blocks = document.querySelectorAll(
          'section[aria-label="Photo Analysis Tool"] div.grid.grid-cols-1.md\\\\:grid-cols-2.gap-6 > div'
        );
        if (!blocks || blocks.length < 2) return null;

        let output = [];
        blocks.forEach(b => {
            const txt = b.innerText.trim();
            if (txt.length > 20) output.push(txt);
        });

        return output.length > 0 ? output : null;
        """

        geo_results = None
        start_time = time.time()

        while time.time() - start_time < 30:
            geo_results = driver.execute_script(poll_geo_js)
            if geo_results:
                break
            time.sleep(0.4)

        if geo_results:
            for block in geo_results:
                print("\n" + block)
        else:
            print("GeoSpy analysis not available.")

        print("\n" + "=" * 60)

    except TimeoutException:
        print("Timed out while waiting for page elements.")
    except Exception as e:
        print(f"Unhandled error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    run_metadata_analyzer()
