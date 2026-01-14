import streamlit as st
import pandas as pd

from scanner import scan_website
from tracker_engine import detect_trackers


def main():

    # --------------------------------------------------
    # Page Configuration
    # --------------------------------------------------
    st.set_page_config(
        page_title="Reverse OSINT – Website Tracking Intelligence",
        layout="wide"
    )

    # --------------------------------------------------
    # Header (UNCHANGED)
    # --------------------------------------------------
    st.markdown(
        "<h1 style='margin-bottom:6px;'>Reverse OSINT – Website Tracking Intelligence</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='color:#9ca3af; max-width:900px;'>"
        "This dashboard explains who is tracking users on a website, "
        "how the tracking is implemented, and what the exposure level means — "
        "based solely on publicly visible website code."
        "</p>",
        unsafe_allow_html=True
    )

    # --------------------------------------------------
    # Input
    # --------------------------------------------------
    url = st.text_input(
        "Target Website URL",
        placeholder="https://www.example.com"
    )

    # --------------------------------------------------
    # Run Analysis
    # --------------------------------------------------
    if st.button("Run Reverse OSINT Analysis"):
        if not url:
            st.warning("Please enter a valid website URL.")
        else:
            with st.spinner("Analyzing website tracking technologies..."):
                scripts = scan_website(url)
                findings = detect_trackers(scripts)

            # ==================================================
            # EXECUTIVE SUMMARY (UPDATED PARAMETERS)
            # ==================================================
            st.divider()
            st.subheader("Executive Summary")

            tracker_count = len(findings)
            categories = set(f["Category"] for f in findings)

            if tracker_count <= 2:
                tracking_level = "LOW"
                summary_text = (
                    f"{tracker_count} tracking technology detected. "
                    "Tracking presence is minimal."
                )
            elif 2 <= tracker_count <= 3 and len(categories) == 1:
                tracking_level = "MEDIUM"
                summary_text = (
                    f"{tracker_count} tracking technologies detected within a single category. "
                    "Tracking is present but limited in scope."
                )
            else:
                tracking_level = "HIGH"
                summary_text = (
                    f"{tracker_count} tracking technologies detected across multiple categories. "
                    "This indicates a strong tracking ecosystem."
                )

            if tracking_level == "HIGH":
                st.error("🔴 High Tracking Presence")
            elif tracking_level == "MEDIUM":
                st.warning("🟡 Medium Tracking Presence")
            else:
                st.success("🟢 Low Tracking Presence")

            st.write(summary_text)

            # ==================================================
            # REFERENCE TABLE — TRACKING CLASSIFICATION RULES
            # ==================================================
            st.subheader("Tracking Classification Reference")

            tracking_rules_df = pd.DataFrame([
                {
                    "Condition": "1–2 trackers found",
                    "Assigned Color": "🟢 Green",
                    "Explanation": "Website shows minimal tracking behavior"
                },
                {
                    "Condition": "2–3 trackers AND same category",
                    "Assigned Color": "🟡 Yellow",
                    "Explanation": "Limited tracking, usually analytics-focused"
                },
                {
                    "Condition": "4+ trackers OR multiple categories",
                    "Assigned Color": "🔴 Red",
                    "Explanation": "Strong and diverse tracking ecosystem detected"
                }
            ])

            st.dataframe(tracking_rules_df, use_container_width=True)

            # ==================================================
            # TRACKER COUNT SUMMARY TABLE
            # ==================================================
            st.subheader("Detected Tracker Summary")

            summary_table = pd.DataFrame([
                {
                    "Total Trackers Detected": tracker_count,
                    "Distinct Categories": len(categories),
                    "Tracking Classification": tracking_level
                }
            ])

            st.dataframe(summary_table, use_container_width=True)

            # ==================================================
            # TRACKING EVIDENCE 
            # ==================================================
            st.divider()
            st.subheader("Detected Tracking Technologies")

            if not findings:
                st.success("No tracking technologies identified.")
            else:
                df = pd.DataFrame(findings)
                st.dataframe(df, use_container_width=True)

            # ==================================================
            # WHAT THESE TECHNOLOGIES DO 
            # ==================================================
            if findings:
                st.divider()
                st.subheader("What These Technologies Do")

                for item in findings:
                    st.markdown(f"""
**{item['Tracker']}** ({item['Company']})  
**Category:** {item['Category']}  
**Detected Using:** {item['Detected Tags']}  

{item['Description']}
""")

            # ==================================================
            # EXPOSURE RISK SEVERITY ASSESSMENT 
            # ==================================================
            st.divider()
            st.subheader("Exposure Risk Severity Assessment")

            risk_reasons = []

            if "Session Replay" in categories:
                risk_reasons.append("Sensitive interaction data may be recorded")

            if len(categories) >= 2:
                risk_reasons.append("Cross-platform correlation possible")

            if "Advertising" in categories and "Session Replay" in categories:
                risk_reasons.append("Behavioral data may be exploited for profiling")

            if tracker_count > 0:
                risk_reasons.append("Tracking logic is actively embedded in website code")

            if len(risk_reasons) >= 3:
                st.error("🔴 High Exposure Risk")
            elif len(risk_reasons) == 2:
                st.warning("🟡 Moderate Exposure Risk")
            else:
                st.success("🟢 Low Exposure Risk")

            # ==================================================
            # EXPOSURE RISK REFERENCE TABLE
            # ==================================================
            st.subheader("Exposure Risk Evaluation Criteria")

            exposure_table = pd.DataFrame([
                {
                    "Risk Factor": "Sensitivity of Information",
                    "Evaluation Basis": "Presence of session replay or interaction recording"
                },
                {
                    "Risk Factor": "Cross-platform Correlation Strength",
                    "Evaluation Basis": "Multiple tracking categories detected"
                },
                {
                    "Risk Factor": "Potential Exploitability",
                    "Evaluation Basis": "Combination of behavioral tracking and advertising"
                },
                {
                    "Risk Factor": "Recency & Visibility of Exposure",
                    "Evaluation Basis": "Tracking logic embedded directly in live website code"
                }
            ])

            st.dataframe(exposure_table, use_container_width=True)

            for reason in risk_reasons:
                st.write("•", reason)


if __name__ == "__main__":
    main()
