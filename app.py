import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="TeamCenter ECN Dashboard", layout="wide", initial_sidebar_state="collapsed")
st.title("⚙️ Engineering Change Notice Dashboard")

# 2. Data Loading & Cleaning (Same robust logic)
@st.cache_data
def load_and_clean_data():
    df = pd.read_csv("teamcenter_data.csv")
    df.columns = df.columns.str.strip()
    
    def determine_status(level):
        lvl_str = str(level).strip()
        if lvl_str == '8': return 'Closed'
        else: return f'Open (Phase {lvl_str})'
            
    df['Dashboard_Status'] = df['Status Lvl'].apply(determine_status)
    df['Primary_Status'] = df['Dashboard_Status'].apply(lambda x: 'Closed' if x == 'Closed' else 'Open')
    
    df['Creation Date'] = pd.to_datetime(df['Creation Date'], errors='coerce')
    df['Date Modified'] = pd.to_datetime(df['Date Modified'], errors='coerce')
    now = pd.Timestamp.now()
    df['End Date'] = df.apply(lambda x: x['Date Modified'] if x['Primary_Status'] == 'Closed' else now, axis=1)
    df['Days Open'] = (df['End Date'] - df['Creation Date']).dt.days.fillna(0).clip(lower=0).astype(int)
    
    return df

try:
    df = load_and_clean_data()
except FileNotFoundError:
    st.error("Data file 'teamcenter_data.csv' not found. Please upload it to your repository.")
    st.stop()

# 3. THE NEW UI: Horizontal Filter Ribbon
st.markdown("### 🔍 Global Filters")

# Create a row of 5 columns for our sleek buttons
f_col1, f_col2, f_col3, f_col4, f_col5 = st.columns(5)

with f_col1:
    search_query = st.text_input("Search", "", placeholder="Search ECN or Keyword...", label_visibility="collapsed")

# Using st.popover to create clean, drop-down checkboxes instead of messy tags
with f_col2:
    with st.popover("📂 Status Phase", use_container_width=True):
        status_options = sorted(df['Dashboard_Status'].unique())
        selected_detailed_status = [stat for stat in status_options if st.checkbox(stat, value=True)]

with f_col3:
    with st.popover("🏢 Division", use_container_width=True):
        div_options = sorted(df['Division'].dropna().unique())
        selected_divisions = [div for div in div_options if st.checkbox(div, value=True)]

with f_col4:
    with st.popover("👤 Owner", use_container_width=True):
        owner_options = sorted(df['Owner'].dropna().unique())
        selected_owners = [own for own in owner_options if st.checkbox(own, value=True)]

with f_col5:
    with st.popover("📁 Program", use_container_width=True):
        prog_options = sorted(df['Program Code'].dropna().unique())
        selected_programs = [prog for prog in prog_options if st.checkbox(prog, value=True)]

# Apply Filters
filtered_df = df[
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

st.divider()

# 4. Metrics & Charts Layout
col1, col2, col3, col4 = st.columns(4)
total_ecns = len(filtered_df)
open_df = filtered_df[filtered_df['Primary_Status'] == 'Open']
open_ecns = len(open_df)
closed_ecns = len(filtered_df[filtered_df['Primary_Status'] == 'Closed'])
avg_days = open_df['Days Open'].mean() if not open_df.empty else 0

col1.metric("Total ECNs", total_ecns)
col2.metric("Active ECNs", open_ecns)
col3.metric("Closed ECNs", closed_ecns)
col4.metric("Avg Aging (Active)", f"{avg_days:.1f} Days")

st.markdown("---")

# Charts Side-by-Side
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    st.markdown("**Avg Days Open by Phase**")
    if not open_df.empty:
        phase_aging = open_df.groupby('Dashboard_Status')['Days Open'].mean().reset_index()
        fig1 = px.bar(phase_aging, x='Dashboard_Status', y='Days Open', text_auto='.1f')
        fig1.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig1, use_container_width=True)

with chart_col2:
    st.markdown("**Active ECNs by Program**")
    if not open_df.empty:
        fig2 = px.pie(open_df, names='Program Code', hole=0.4)
        fig2.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=300)
        st.plotly_chart(fig2, use_container_width=True)

st.divider()

# 5. Clean Data View
st.subheader("ECN Tracking Log")
columns_to_display = ['ECN Number', 'Program Code', 'Dashboard_Status', 'Days Open', 'Description', 'Division', 'Owner']
st.dataframe(filtered_df[columns_to_display], use_container_width=True, hide_index=True)
