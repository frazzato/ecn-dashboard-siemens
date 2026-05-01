# ⚙️ Teamcenter ECN Tracking Dashboard

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](YOUR_STREAMLIT_APP_URL_HERE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

A dynamic, serverless engineering dashboard built to visualize Siemens Teamcenter Engineering Change Notice (ECN) exports. 

This application provides real-time cycle time analytics and bottleneck identification through a custom, high-performance web interface. It strictly avoids generic "spreadsheet embed" styling in favor of a native, engineered frontend that maintains the structural integrity of the original CSV data layout.

---

## 🚀 Live Demo

https://ecn-dashboard-siemens-jmjbmhigqs5arrompjbsox.streamlit.app/

---

## ✨ Core Features

* **Custom Engineered UI:** Utilizes a top-bar horizontal ribbon with popover menus for an uncluttered, modern enterprise feel.
* **Smart Phase Mapping:** Automatically translates numeric Teamcenter status codes (e.g., `-2`, `4`) into readable business logic (`Engineering`, `Purchase`). Enforces strict phase gate logic where only Level 8 is considered "Closed."
* **Cycle Time Analytics:** Dynamically calculates "Days Open" from creation dates, providing instant visibility into aging ECNs.
* **Interactive Visualizations:** Integrated Plotly charts provide real-time bottleneck analysis (Avg Days Open by Phase) and workload distribution (Active ECNs by Program).
* **1-Click Offline Export:** Filter the dashboard to specific criteria and instantly download a clean `.csv` for offline leadership reporting.

---

## 🏗️ Architecture & Tech Stack

This project uses a lightweight, two-tier architecture relying on GitHub for data storage and version control, and Streamlit for the frontend application layer.

* **Frontend & Logic:** [Streamlit](https://streamlit.io/)
* **Data Manipulation:** [Pandas](https://pandas.pydata.org/)
* **Data Visualization:** [Plotly Express](https://plotly.com/python/)
* **Database / Hosting:** GitHub Repository + Streamlit Community Cloud

### Repository Structure
```text
ecn-dashboard/
│
├── app.py                 # Main Streamlit application and UI logic
├── requirements.txt       # Python dependencies
├── teamcenter_data.csv    # Raw data export from Siemens Teamcenter
└── README.md              # Project documentation
