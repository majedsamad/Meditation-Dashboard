import pandas as pd

# --- YOUR RAW DATA HERE ---
# Edit this list with your habit phases. 
# Format: Start Date, End Date, and Avg Hours per day during that period
habit_phases = [
    # (Start, End, Hours_Per_Day)
    ("2023-01-01", "2023-03-31", 0.5),  # Early year: 30 mins/day
    ("2023-04-01", "2023-06-14", 1.0),  # Pre-retreat ramp up: 1 hour/day
    ("2023-06-26", "2023-12-31", 0.75), # Post-retreat maintenance: 45 mins
]

# --- PROCESSING ---
all_daily_rows = []

for start, end, hours in habit_phases:
    # Create a range of dates for this phase
    dates = pd.date_range(start=start, end=end)
    
    # Create a row for every single day in that range
    for d in dates:
        all_daily_rows.append({
            "Date": d.strftime("%Y-%m-%d"),
            "Hours": hours
        })

# --- EXPORT ---
df = pd.DataFrame(all_daily_rows)

# Optional: Ensure no duplicate dates if your ranges accidentally overlapped
# We group by Date and sum the hours just in case
df = df.groupby("Date", as_index=False)["Hours"].sum()

df.to_csv("daily_log.csv", index=False)
print(f"✅ daily_log.csv created with {len(df)} rows!")
print(df.head())