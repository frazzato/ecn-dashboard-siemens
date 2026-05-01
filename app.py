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

# 4. Custom Engineered Filters
st.sidebar.header("🔍 Filters")

# Global Search
search_query = st.sidebar.text_input("Search ECN or Keyword", "")

# Custom Dropdown for Programs using st.popover
with st.sidebar.popover("📁 Filter by Program Code", use_container_width=True):
    programs = sorted(df['Program Code'].dropna().unique())
    prog_selections = {}
    # Create a clean checklist inside the dropdown
    for prog in programs:
        prog_selections[prog] = st.checkbox(prog, value=True) # Default all to checked
    
    # Extract only the checked items
    selected_programs = [p for p, is_checked in prog_selections.items() if is_checked]

# Custom Dropdown for Division using st.popover
with st.sidebar.popover("🏢 Filter by Division", use_container_width=True):
    divisions = sorted(df['Division'].dropna().unique())
    div_selections = {}
    for div in divisions:
        div_selections[div] = st.checkbox(div, value=True)
        
    selected_divisions = [d for d, is_checked in div_selections.items() if is_checked]

# --- Apply the Filtering Logic ---
filtered_df = df.copy()

# Apply Advanced Filters
filtered_df = filtered_df[
    (filtered_df['Program Code'].isin(selected_programs)) &
    (filtered_df['Division'].isin(selected_divisions))
]

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
