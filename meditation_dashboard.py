import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_js_eval import streamlit_js_eval
from convert_daily import get_daily_log_df

st.set_page_config(page_title="Majed's Meditation Analytics", layout="wide")

# --- 1. LOAD DATA ---
try:
    df_retreats = pd.read_csv("retreats.csv")
    df_daily = get_daily_log_df()  # Generate daily log directly
    df_daily["Type"] = "Daily Practice"
except FileNotFoundError:
    st.error("retreats.csv not found. Please ensure the file exists.")
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
        # Determine hours based on retreat kind
        # Served = 4 hours (light practice), Sat = 12 hours (intense practice)
        daily_hours = 4.0 if row["Kind"] == "Served" else 12.0
        
        retreat_daily_rows.append({
            "Date": d, 
            "Hours": daily_hours, 
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

# Retreat Counts by Type with Icons
st.subheader("Retreat Breakdown")
unique_retreats = sorted(df_retreats["Name"].unique())

# Map retreat names to icons
def get_retreat_icon(name):
    if "10-day (part-time)" in name:
        return "5️⃣"
    elif "10-day" in name:
        return "🔟"
    elif "Satipatthana" in name:
        return "8️⃣"
    elif "3-day" in name:
        return "3️⃣"
    else:
        return "📍"

cols = st.columns(len(unique_retreats))

for idx, r_name in enumerate(unique_retreats):
    # Filter for this specific retreat name
    df_subset = df_retreats[df_retreats["Name"] == r_name]
    
    # Count Sat vs Served
    sat_count = len(df_subset[df_subset["Kind"] == "Sat"])
    served_count = len(df_subset[df_subset["Kind"] == "Served"])
    
    # Get icon for this retreat type
    icon = get_retreat_icon(r_name)
    
    with cols[idx]:
        st.metric(f"{icon} {r_name}", f"{sat_count} Sat / {served_count} Served")

# Define specific colors
color_map = {
    "Sat": "#5D3FD3",    # Deep Purple
    "Served": "#FF4B4B"  # Red/Orange
}

def get_icon(name):
    # Mapping logic for emojis
    if "10-day (part-time)" in name:
        return "5️⃣"
    elif "10-day" in name:
        return "🔟"
    elif "Satipatthana" in name:
        return "8️⃣"
    elif "3-day" in name:
        return "3️⃣"
    else:
        return "📍"

# Apply icon mapping
df_retreats["Icon"] = df_retreats.apply(
    lambda row: get_icon(row["Name"]), axis=1
)

# 2. Create Single Row Timeline
# We use a timeline for the background bars (duration)
hover_cols = [c for c in ["Name", "Link", "Location", "Duration_Days"] if c in df_retreats.columns]
fig_single = px.timeline(
    df_retreats,
    x_start="Start",
    x_end=df_retreats["Start"] + pd.Timedelta(days=20),
    y=["Retreats"] * len(df_retreats), # Constant value to flatten rows
    color="Kind",
    color_discrete_map=color_map,
    opacity=0.9,
    hover_data=hover_cols,
)

# Overlay Icons using Scatter (Text Mode)
# This ensures icons are always visible regardless of retreat duration
fig_single.add_scatter(
    x=df_retreats["Start"] + pd.Timedelta(days=10), # Center the icon
    y=["Retreats"] * len(df_retreats),
    mode="text",
    text=df_retreats["Icon"],
    textfont=dict(size=20), # Fixed size for visibility
    showlegend=False,
    hoverinfo="skip" # Tooltip already provided by the bars
)

fig_single.update_layout(
    height=250, # Compact height
    yaxis=dict(visible=False), # Hide "Retreats" label to save space
    xaxis_title="Date",
    xaxis=dict(
        tickmode="linear",
        tick0="2009-01-01",
        dtick="M12", # Yearly ticks
        tickformat="%Y", # Show only the year,
        showgrid=True,
        gridcolor="rgba(255,255,255,.1)" # Subtle vertical lines
    ),
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.5,
        xanchor="left",
        x=0.0,
        title=""
    )
)

# Responsive Zoom for Mobile
screen_width = streamlit_js_eval(js_expressions='window.innerWidth', key='SCR_WIDTH')

# Default to "zoomed out" (show everything)
# If mobile (< 768px), default to showing only the last few years
if screen_width is not None and screen_width < 768:
    max_date = df_retreats["Start"].max() + pd.Timedelta(days=30) # A bit of buffer
    min_date = max_date - pd.DateOffset(years=3) # Show last 3 years
    fig_single.update_xaxes(range=[min_date, max_date])

st.plotly_chart(fig_single, width='stretch')

st.divider()

# Calculate Breakdowns
total_hours = df_monthly_total['Hours'].sum()
daily_hours = df_daily['Hours'].sum()
if not df_retreat_expanded.empty:
    sat_hours = df_retreat_expanded[df_retreat_expanded["Kind"] == "Sat"]["Hours"].sum()
    served_hours = df_retreat_expanded[df_retreat_expanded["Kind"] == "Served"]["Hours"].sum()
else:
    sat_hours = 0
    served_hours = 0


# Chart 1: Cumulative Progress (Area Chart)
st.subheader("Cumulative Hours")

# Top Metrics
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    st.metric("Total Life Hours", f"{total_hours:,.0f}")
with col2:
    st.metric("Daily Practice", f"{daily_hours:,.0f}")
with col3:
    st.metric("Retreats (Sat)", f"{sat_hours:,.0f}")
with col4:
    st.metric("Retreats (Served)", f"{served_hours:,.0f}")
with col5:
    # Calculate average yearly hours
    years = (df_monthly_total["Date"].max() - df_monthly_total["Date"].min()).days / 365.25
    avg_annual = df_monthly_total["Hours"].sum() / years
    st.metric("Avg Hours / Year", f"{avg_annual:,.0f}")
with col6:
    st.metric("Years of Practice", f"{years:.0f}")

fig_cum = px.area(
    df_monthly_total, 
    x="Date", 
    y="Cumulative Hours",
    title="Total Accumulated Practice",
    color_discrete_sequence=["#5D3FD3"]
)
st.plotly_chart(fig_cum, width='stretch')

st.divider()

st.subheader("Retreat Locations")

# Ensure Duration_Days exists
if "Duration_Days" not in df_retreats.columns:
    df_retreats["Duration_Days"] = (df_retreats["End"] - df_retreats["Start"]).dt.days

# Aggregate by location and center: total days and build a detailed breakdown for hover
def build_location_summary(group):
    total_days = group["Duration_Days"].sum()
    center = group["Center"].iloc[0]  # Get center name (same for all rows in group)
    
    # Build breakdown by Name and Kind
    breakdown_lines = []
    for (name, kind), sub in group.groupby(["Name", "Kind"]):
        count = len(sub)
        breakdown_lines.append(f"{name}: {count} {kind}")
    
    breakdown_text = "<br>".join(sorted(breakdown_lines))
    
    return pd.Series({
        "TotalDays": total_days,
        "Breakdown": breakdown_text,
        "RetreatCount": len(group),
        "Center": center
    })

df_location_agg = df_retreats.groupby(["Lat", "Lon"]).apply(build_location_summary, include_groups=False).reset_index()

# Color palette for centers
center_colors = {
    "Dhamma Kunja": "#5D3FD3",      # Deep Purple
    "Dhamma Vaddhana": "#2E8B57",   # Sea Green
    "Dhamma Dipa": "#DC143C",       # Crimson
    "Dhamma Mahavana": "#FF6B35",   # Orange
    "Dhamma Siri": "#1E90FF",       # Dodger Blue
}

# Create the map with one circle per location, size by total days, color by center
fig_map = px.scatter_map(
    df_location_agg,
    lat="Lat",
    lon="Lon",
    size="TotalDays",
    size_max=30,  # Max bubble size
    color="Center",
    color_discrete_map=center_colors,
    opacity=0.7,
    zoom=1,
    height=500,
    title="",
    hover_name="Center",
    custom_data=["TotalDays", "RetreatCount", "Breakdown"],
    hover_data={
        "TotalDays": False,
        "RetreatCount": False,
        "Center": False,
        "Lat": False,
        "Lon": False
    }
)

# Add custom hover template with breakdown - use selector to update only scattermap traces
for trace in fig_map.data:
    trace.hovertemplate = (
        "<b>%{hovertext}</b><br>" +
        "<b>Total Days:</b> %{customdata[0]}<br>" +
        "<b>Retreats:</b> %{customdata[1]}<br><br>" +
        "%{customdata[2]}<extra></extra>"
    )

# Add text labels for center names using graph_objects
import plotly.graph_objects as go

fig_map.add_trace(go.Scattermap(
    lat=df_location_agg["Lat"] - 0.5,  # Offset slightly below the circles
    lon=df_location_agg["Lon"],
    mode="text",
    text=df_location_agg["Center"],
    textfont=dict(size=12, color="#333333"),
    showlegend=False,
    hoverinfo="skip"
))

# Use 'open-street-map' style (no API key required)
fig_map.update_layout(
    mapbox_style="open-street-map",
    margin={"r":0,"t":40,"l":0,"b":0},
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
        title=""
    )
)

st.plotly_chart(fig_map, width='stretch')