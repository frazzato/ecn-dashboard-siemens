import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="TeamCenter ECN Dashboard", layout="wide")
st.title("⚙️ Engineering Change Notice Dashboard")
st.markdown("Live view of Siemens TeamCenter exports with cycle time analytics.")

# 2. Data Loading & Cleaning
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("teamcenter_data.csv")
    df.columns = df.columns.str.strip()
    
    # Custom Status Logic
    def determine_status(level):
        lvl_str = str(level).strip()
        if lvl_str == '8': return 'Closed'
        else: return f'Open (Phase {lvl_str})'
            
    df['Dashboard_Status'] = df['Status Lvl'].apply(determine_status)
    df['Primary_Status'] = df['Dashboard_Status'].apply(lambda x: 'Closed' if x == 'Closed' else 'Open')
    
    # Cycle Time Calculation
    # Convert dates to datetime objects
    df['Creation Date'] = pd.to_datetime(df['Creation Date'], errors='coerce')
    df['Date Modified'] = pd.to_datetime(df['Date Modified'], errors='coerce')
    
    # If closed, age is (Date Modified - Creation). If open, age is (Today - Creation).
    now = pd.Timestamp.now()
    df['End Date'] = df.apply(lambda x: x['Date Modified'] if x['Primary_Status'] == 'Closed' else now, axis=1)
    df['Days Open'] = (df['End Date'] - df['Creation Date']).dt.days
    # Fill any missing/negative values with 0
    df['Days Open'] = df['Days Open'].fillna(0).clip(lower=0).astype(int)
    
    return df

try:
    df = load_and_clean_data()
except FileNotFoundError:
    st.error("Data file 'teamcenter_data.csv' not found. Please upload it to your repository.")
    st.stop()

# 3. Enterprise Sidebar Filters
st.sidebar.header("🔍 Global Search & Filter")
search_query = st.sidebar.text_input("Search ECN, Program, or Keyword", "")

with st.sidebar.expander("📂 Status", expanded=True):
    selected_primary_status = st.multiselect("Open / Closed", sorted(df['Primary_Status'].unique()), default=sorted(df['Primary_Status'].unique()))
    selected_detailed_status = st.multiselect("Phase Level", sorted(df['Dashboard_Status'].unique()), default=sorted(df['Dashboard_Status'].unique()))

with st.sidebar.expander("🏢 Organization", expanded=False):
    selected_divisions = st.multiselect("Division", sorted(df['Division'].dropna().unique()), default=sorted(df['Division'].dropna().unique()))
    selected_owners = st.multiselect("Owning User", sorted(df['Owner'].dropna().unique()), default=sorted(df['Owner'].dropna().unique()))

with st.sidebar.expander("📁 Item Revision / Program", expanded=False):
    selected_programs = st.multiselect("Program Code", sorted(df['Program Code'].dropna().unique()), default=sorted(df['Program Code'].dropna().unique()))

# Apply Filters
filtered_df = df[
    (df['Primary_Status'].isin(selected_primary_status)) &
    (df['Dashboard_Status'].isin(selected_detailed_status)) &
    (df['Division'].isin(selected_divisions)) &
    (df['Owner'].isin(selected_owners)) &
    (df['Program Code'].isin(selected_programs))
]

if search_query:
    mask = (
        filtered_df['ECN Number'].astype(str).str.contains(search_query, case=False, na=False) |
        filtered_df['Description'].astype(str).str.contains(search_query, case=False, na=False) |
        filtered_df['Program Code'].astype(str).str.contains(search_query, case=False, na=False)
    )
    filtered_df = filtered_df[mask]

# 4. High-Level Metrics (Now with Cycle Time)
st.subheader("KPI Overview")
col1, col2, col3, col4 = st.columns(4)

total_ecns = len(filtered_df)
open_ecns = len(filtered_df[filtered_df['Primary_Status'] == 'Open'])
closed_ecns = len(filtered_df[filtered_df['Primary_Status'] == 'Closed'])
# Calculate Average Days Open for currently filtered active ECNs
open_df = filtered_df[filtered_df['Primary_Status'] == 'Open']
avg_days = open_df['Days Open'].mean() if not open_df.empty else 0

col1.metric("Total ECNs", total_ecns)
col2.metric("Active ECNs", open_ecns)
col3.metric("Closed ECNs", closed_ecns)
col4.metric("Avg Aging (Active)", f"{avg_days:.1f} Days", help="Average days open for active ECNs")

st.divider()

# 5. Dynamic Interactive Charts (Plotly)
st.subheader("📊 Cycle Time & Workload Analytics")
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Bottleneck Analysis: Avg Days Open by Phase**")
    if not open_df.empty:
        # Group by phase and calculate average age
        phase_aging = open_df.groupby('Dashboard_Status')['Days Open'].mean().reset_index()
        fig1 = px.bar(
            phase_aging, x='Dashboard_Status', y='Days Open', 
            color='Dashboard_Status', text_auto='.1f',
            labels={'Dashboard_Status': 'Phase', 'Days Open': 'Avg Days Open'}
        )
        fig1.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No active ECNs match the current filter.")

with chart_col2:
    st.markdown("**Workload Distribution: Active ECNs by Program**")
    if not open_df.empty:
        fig2 = px.pie(
            open_df, names='Program Code', hole=0.4, 
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig2.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No active ECNs match the current filter.")

st.divider()

# 6. Clean Data View
st.subheader("ECN Tracking Log")
columns_to_display = [
    'ECN Number', 'Program Code', 'Dashboard_Status', 
    'Days Open', 'Description', 'Division', 'Owner'
]

st.dataframe(
    filtered_df[columns_to_display],
    use_container_width=True,
    hide_index=True
)
