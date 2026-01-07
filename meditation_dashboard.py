import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Meditation Analytics (Monthly)", layout="wide")

# --- 1. LOAD DATA ---
try:
    df_retreats = pd.read_csv("retreats.csv")
    df_daily = pd.read_csv("daily_log.csv")
    df_daily["Type"] = "Daily Practice"
except FileNotFoundError:
    st.error("CSV files not found. Please run your conversion scripts first.")
    st.stop()

# Ensure datetime formats
df_retreats["Start"] = pd.to_datetime(df_retreats["Start"])
df_retreats["End"] = pd.to_datetime(df_retreats["End"])
df_daily["Date"] = pd.to_datetime(df_daily["Date"])

# --- 2. EXPAND RETREATS (Crucial for split months) ---
retreat_daily_rows = []
for _, row in df_retreats.iterrows():
    # Create a daily range for the retreat duration
    r_dates = pd.date_range(start=row["Start"], end=row["End"] - pd.Timedelta(days=1))
    
    for d in r_dates:
        retreat_daily_rows.append({
            "Date": d, 
            "Hours": 12.0,  # Assumption: 12 hours/day on retreat
            "Type": "Retreat",
            "Kind": row["Kind"] # Include Sat vs Served
        })

df_retreat_expanded = pd.DataFrame(retreat_daily_rows)

# --- 3. MERGE & AGGREGATE TO MONTHLY ---

# Combine Daily Log + Expanded Retreats
# We only need the common columns for the combined total
df_combined = pd.concat([df_daily, df_retreat_expanded], ignore_index=True)

# Set Date as index to allow resampling
# This is mainly for the "Total Life" calculations
df_monthly_total = df_combined.set_index("Date").resample("MS")[["Hours"]].sum().reset_index()

# Calculate Cumulative Sum on the MONTHLY data
df_monthly_total["Cumulative Hours"] = df_monthly_total["Hours"].cumsum()

# --- 4. PREPARE RETREATS SPECIFIC DATA ---
# Aggregate retreats by Month and Kind (Sat vs Served)
if not df_retreat_expanded.empty:
    df_retreats_monthly = df_retreat_expanded.groupby(
        [pd.Grouper(key="Date", freq="MS"), "Kind"]
    )[["Hours"]].sum().reset_index()
else:
    df_retreats_monthly = pd.DataFrame(columns=["Date", "Kind", "Hours"])


# --- 5. VISUALIZATION ---

st.title("🧘 Long-Term Meditation History")

# Top Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Life Hours", f"{df_monthly_total['Hours'].sum():,.0f}")
with col2:
    st.metric("Total Retreats", len(df_retreats))
with col3:
    # Calculate average yearly hours
    years = (df_monthly_total["Date"].max() - df_monthly_total["Date"].min()).days / 365.25
    avg_annual = df_monthly_total["Hours"].sum() / years
    st.metric("Avg Hours / Year", f"{avg_annual:,.0f}")

st.divider()

# Chart 1: Cumulative Progress (Area Chart)
st.subheader("Cumulative Hours (17 Years)")
fig_cum = px.area(
    df_monthly_total, 
    x="Date", 
    y="Cumulative Hours",
    title="Total Accumulated Practice",
    color_discrete_sequence=["#5D3FD3"]
)
st.plotly_chart(fig_cum, use_container_width=True)

# Chart 2: Retreats Over Time
st.subheader("Retreats Over Time")

# Define specific colors
color_map = {
    "Sat": "#5D3FD3",    # Deep Purple
    "Served": "#FF4B4B"  # Red/Orange
}

fig_vol = px.bar(
    df_retreats_monthly,
    x="Date",
    y="Hours",
    title="Retreats over time",
    color="Kind",
    color_discrete_map=color_map,
    opacity=0.9
)

# Move legend inside the chart
fig_vol.update_layout(
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(255, 255, 255, 0.5)"
    )
)

st.plotly_chart(fig_vol, use_container_width=True)

# --- NEW: MAP VISUALIZATION ---
st.divider()
st.subheader("Retreat Locations")

# We need the 'Duration_Days' for the bubble size. 
# If it wasn't saved in the CSV, recalculate it quickly:
if "Duration_Days" not in df_retreats.columns:
    df_retreats["Duration_Days"] = (df_retreats["End"] - df_retreats["Start"]).dt.days

# Create the map
fig_map = px.scatter_mapbox(
    df_retreats,
    lat="Lat",
    lon="Lon",
    hover_name="Name",
    hover_data={"Start": True, "Duration_Days": True, "Lat": False, "Lon": False},
    size="Duration_Days",       # Bigger bubbles for longer retreats
    color="Duration_Days",      # Color gradient based on duration
    color_continuous_scale=px.colors.sequential.Sunsetdark,
    zoom=1,                     # Start zoomed out to see the world
    height=500,
    title="Retreat Geography"
)

# Use 'open-street-map' style (no API key required)
fig_map.update_layout(mapbox_style="open-street-map")
fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0}) # Tight margins

st.plotly_chart(fig_map, use_container_width=True)