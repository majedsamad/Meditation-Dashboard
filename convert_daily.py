import pandas as pd

# --- YOUR RAW DATA HERE ---
# Edit this list with your habit phases. 
# Format: Start Date, End Date, and Avg Hours per day during that period
habit_phases = [
    # (Start, End, Hours_Per_Day)
    ("2009-07-01", "2012-03-01", 0.25),
    ("2012-03-01", "2012-12-31", 2),
    ("2013-01-01", "2022-12-31", 0.25),
    ("2023-01-01", "2023-12-31", 1),
    ("2024-01-01", "2025-12-31", 2),
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