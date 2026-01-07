import pandas as pd
from datetime import timedelta

# --- YOUR RAW DATA HERE ---
# Edit this list with your actual retreat history
raw_retreats = [
    {"Name": "10-day", "Start": "2009-07-01", "Days": 10, "Lat": 51.93717047288657, "Lon": -2.7183688422482426, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2010-06-01", "Days": 10, "Lat": 51.93717047288657, "Lon": -2.7183688422482426, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2011-06-01", "Days": 10, "Lat": 34.13290739801991, "Lon": -116.16958440882196, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2012-07-01", "Days": 10, "Lat": 34.13290739801991, "Lon": -116.16958440882196, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2012-12-01", "Days": 10, "Lat": 34.13290739801991, "Lon": -116.16958440882196, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2013-09-01", "Days": 10, "Lat": 34.13290739801991, "Lon": -116.16958440882196, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2014-09-01", "Days": 10, "Lat": 34.13290739801991, "Lon": -116.16958440882196, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2015-12-01", "Days": 10, "Lat": 34.13290739801991, "Lon": -116.16958440882196, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2017-12-01", "Days": 10, "Lat": 46.551094113518346, "Lon": -122.68237978383321, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2019-02-01", "Days": 10, "Lat": 46.551094113518346, "Lon": -122.68237978383321, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2021-12-01", "Days": 10, "Lat": 46.551094113518346, "Lon": -122.68237978383321, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2022-12-01", "Days": 10, "Lat": 46.551094113518346, "Lon": -122.68237978383321, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2023-12-01", "Days": 10, "Lat": 46.551094113518346, "Lon": -122.68237978383321, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2025-02-01", "Days": 10, "Lat": 46.551094113518346, "Lon": -122.68237978383321, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2025-12-01", "Days": 10, "Lat": 46.551094113518346, "Lon": -122.68237978383321, "Kind": "Sat"},
    {"Name": "Satipatthana", "Start": "2012-03-01", "Days": 8, "Lat": 34.13290739801991, "Lon": -116.16958440882196, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2020-02-01", "Days": 5, "Lat": 46.551094113518346, "Lon": -122.68237978383321, "Kind": "Sat"},
    {"Name": "3-day", "Start": "2023-08-01", "Days": 3, "Lat": 46.551094113518346, "Lon": -122.68237978383321, "Kind": "Sat"},
    {"Name": "10-day", "Start": "2017-01-01", "Days": 10, "Lat": 37.21916830190468, "Lon": -119.48214720000388, "Kind": "Served"},
    {"Name": "10-day", "Start": "2024-07-01", "Days": 10, "Lat": 32.49103546489227, "Lon": -96.292384084562, "Kind": "Served"},
    {"Name": "3-day", "Start": "2011-09-01", "Days": 3, "Lat": 34.13290739801991, "Lon": -116.16958440882196, "Kind": "Served"},
    {"Name": "Satipatthana", "Start": "2013-03-01", "Days": 8, "Lat": 34.13290739801991, "Lon": -116.16958440882196, "Kind": "Served"},
    {"Name": "3-day", "Start": "2023-06-01", "Days": 3, "Lat": 46.551094113518346, "Lon": -122.68237978383321, "Kind": "Served"},
]

# --- PROCESSING ---
processed_data = []

for r in raw_retreats:
    start_date = pd.to_datetime(r["Start"])
    end_date = start_date + timedelta(days=r["Days"]) 
    
    processed_data.append({
        "Name": r["Name"],
        "Start": start_date.strftime("%Y-%m-%d"),
        "End": end_date.strftime("%Y-%m-%d"),
        "Duration_Days": r["Days"], # Useful for map bubble size
        "Lat": r["Lat"],
        "Lon": r["Lon"],
        "Kind": r["Kind"]
    })

# --- EXPORT ---
df = pd.DataFrame(processed_data)
df.to_csv("retreats.csv", index=False)
print("✅ retreats.csv updated with locations!")