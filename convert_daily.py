import pandas as pd
from datetime import date

# --- YOUR RAW DATA HERE ---
# Edit this list with your habit phases. 
# Format: Start Date, End Date, and Avg Hours per day during that period
# Use "current" for the end date to indicate today's date
habit_phases = [
    # (Start, End, Hours_Per_Day)
    ("2009-07-01", "2012-03-01", 0.25),
    ("2012-03-01", "2012-12-31", 2),
    ("2013-01-01", "2022-12-31", 0.25),
    ("2023-01-01", "2023-12-31", 1),
    ("2024-01-01", "current", 2),
]


def get_daily_log_df() -> pd.DataFrame:
    """
    Generate the daily log DataFrame from habit_phases.
    Handles the special keyword "current" by converting it to today's date.
    
    Returns:
        pd.DataFrame: DataFrame with columns ["Date", "Hours"]
    """
    all_daily_rows = []
    today = date.today().strftime("%Y-%m-%d")

    for start, end, hours in habit_phases:
        # Handle "current" keyword by replacing with today's date
        if end == "current":
            end = today
        
        # Create a range of dates for this phase
        dates = pd.date_range(start=start, end=end)
        
        # Create a row for every single day in that range
        for d in dates:
            all_daily_rows.append({
                "Date": d.strftime("%Y-%m-%d"),
                "Hours": hours
            })

    df = pd.DataFrame(all_daily_rows)

    # Ensure no duplicate dates if your ranges accidentally overlapped
    # We group by Date and sum the hours just in case
    df = df.groupby("Date", as_index=False)["Hours"].sum()
    
    return df


# Allow running as a standalone script for testing
if __name__ == "__main__":
    df = get_daily_log_df()
    print(f"✅ Generated daily log with {len(df)} rows!")
    print(df.head())
    print(df.tail())