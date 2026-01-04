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
            "Type": "Retreat"
        })

df_retreat_expanded = pd.DataFrame(retreat_daily_rows)

# --- 3. MERGE & AGGREGATE TO MONTHLY ---

# Combine Daily Log + Expanded Retreats
df_combined = pd.concat([df_daily, df_retreat_expanded])

# Set Date as index to allow resampling
df_combined = df_combined.set_index("Date")

# >>>> THE NEW STEP: Resample to Month Start ('MS') <<<<
# We sum the hours for every month.
df_monthly = df_combined.resample("MS")[["Hours"]].sum().reset_index()

# Calculate Cumulative Sum on the MONTHLY data
df_monthly["Cumulative Hours"] = df_monthly["Hours"].cumsum()

# Calculate Rolling Average (e.g., 6-month moving average of monthly hours)
df_monthly["6-Month Avg"] = df_monthly["Hours"].rolling(window=6).mean()

# --- 4. VISUALIZATION ---

st.title("🧘 Long-Term Meditation History")

# Top Metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Life Hours", f"{df_monthly['Hours'].sum():,.0f}")
with col2:
    st.metric("Total Retreats", len(df_retreats))
with col3:
    # Calculate average yearly hours
    years = (df_monthly["Date"].max() - df_monthly["Date"].min()).days / 365.25
    avg_annual = df_monthly["Hours"].sum() / years
    st.metric("Avg Hours / Year", f"{avg_annual:,.0f}")

st.divider()

# Chart 1: Cumulative Progress (Area Chart)
st.subheader("Cumulative Hours (17 Years)")
fig_cum = px.area(
    df_monthly, 
    x="Date", 
    y="Cumulative Hours",
    title="Total Accumulated Practice",
    color_discrete_sequence=["#5D3FD3"]
)
st.plotly_chart(fig_cum, use_container_width=True)

# Chart 2: Monthly Consistency (Bar Chart)
st.subheader("Monthly Activity Volume")
# We can overlay the rolling average to show trends
fig_vol = px.bar(
    df_monthly,
    x="Date",
    y="Hours",
    title="Hours per Month",
    color_discrete_sequence=["#A9A9A9"], # Grey for bars
    opacity=0.6
)

# Add the trendline
fig_vol.add_scatter(
    x=df_monthly["Date"], 
    y=df_monthly["6-Month Avg"], 
    mode='lines', 
    name='6-Month Trend',
    line=dict(color='#FF4B4B', width=3)
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