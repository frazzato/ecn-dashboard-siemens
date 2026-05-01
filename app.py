import streamlit as st
import pandas as pd

# 1. Page Configuration for a Modern, Engineered Look
st.set_page_config(page_title="TeamCenter ECN Dashboard", layout="wide")
st.title("⚙️ Engineering Change Notice Dashboard")
st.markdown("Live view of Siemens TeamCenter exports tracked by Program and Phase Level.")

# 2. Data Loading & Cleaning
@st.cache_data
def load_and_clean_data():
    # Load the CSV. In GitHub, if the file is in the same folder, just use the filename.
    df = pd.read_csv("teamcenter_data.csv")
    
    # Clean headers (removes accidental spaces from TeamCenter exports like ' Status Lvl')
    df.columns = df.columns.str.strip()
    
    # 3. Apply Custom Status Logic
    # Level 8 = Closed. Anything else = Open (Phase X)
    def determine_status(level):
        lvl_str = str(level).strip()
        if lvl_str == '8':
            return 'Closed'
        else:
            return f'Open (Phase {lvl_str})'
            
    df['Dashboard_Status'] = df['Status Lvl'].apply(determine_status)
    return df

try:
    df = load_and_clean_data()
except FileNotFoundError:
    st.error("Data file 'teamcenter_data.csv' not found. Please upload it to your repository.")
    st.stop()

# 4. Advanced Sidebar Filters
st.sidebar.header("🔍 Search & Filter")

# 4a. Global Search Bar
search_query = st.sidebar.text_input("Search ECN Number or Keyword", "")

# 4b. Status Toggle (Looks like modern buttons instead of a dropdown)
status_toggle = st.sidebar.radio(
    "Quick Status Filter", 
    ["All Active & Closed", "Open (All Phases)", "Closed"],
    horizontal=True
)

# 4c. Expandable Advanced Filters
with st.sidebar.expander("⚙️ Advanced Parameters", expanded=False):
    # Program Filter
    programs = sorted(df['Program Code'].dropna().unique())
    selected_programs = st.multiselect("Program Code", programs, default=programs)

    # Division Filter
    divisions = sorted(df['Division'].dropna().unique())
    selected_divisions = st.multiselect("Division", divisions, default=divisions)

# --- Apply the Filtering Logic ---
filtered_df = df.copy()

# Apply Status Toggle
if status_toggle == "Open (All Phases)":
    filtered_df = filtered_df[filtered_df['Dashboard_Status'].str.contains('Open')]
elif status_toggle == "Closed":
    filtered_df = filtered_df[filtered_df['Dashboard_Status'] == 'Closed']

# Apply Advanced Filters
filtered_df = filtered_df[
    (filtered_df['Program Code'].isin(selected_programs)) &
    (filtered_df['Division'].isin(selected_divisions))
]

# Apply Text Search (checks both ECN Number and Description)
if search_query:
    filtered_df = filtered_df[
        filtered_df['ECN Number'].astype(str).str.contains(search_query, case=False, na=False) |
        filtered_df['Description'].astype(str).str.contains(search_query, case=False, na=False)
    ]
# 5. High-Level Engineering Metrics
st.subheader("ECN Overview")
col1, col2, col3, col4 = st.columns(4)

total_ecns = len(filtered_df)
closed_ecns = len(filtered_df[filtered_df['Dashboard_Status'] == 'Closed'])
open_ecns = total_ecns - closed_ecns

col1.metric("Total ECNs", total_ecns)
col2.metric("Open ECNs", open_ecns)
col3.metric("Closed ECNs", closed_ecns)
# Placeholder for Cost once added to your TeamCenter export
col4.metric("Cost in Purchase Impact", "$0.00", help="Requires Cost column in export")

st.divider()

# 6. Clean Data View (Maintaining Original Layout Structure)
st.subheader("ECN Tracking Log")

# Select specific columns to display to keep the dashboard uncluttered
columns_to_display = [
    'ECN Number', 'Program Code', 'Dashboard_Status', 
    'Description', 'Division', 'Owner', 'Creation Date'
]

# Render as a native web component, strictly avoiding Google Sheets/Stitch styling
st.dataframe(
    filtered_df[columns_to_display],
    use_container_width=True,
    hide_index=True
)
