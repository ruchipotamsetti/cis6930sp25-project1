import duckdb
import argparse
from datetime import datetime
from geopy.distance import geodesic
from sodapy import Socrata
import json

# Initialize DuckDB connection
db_conn = duckdb.connect("incidents.duckdb")

# Create tables in DuckDB
db_conn.execute("""
CREATE TABLE IF NOT EXISTS traffic_crashes (
    case_number VARCHAR,
    accident_date TIMESTAMP,
    totalpeopleinvolved INTEGER,
    longitude DOUBLE,
    latitude DOUBLE
)
""")

db_conn.execute("""
CREATE TABLE IF NOT EXISTS crime_records (
    case_number VARCHAR,
    offense_date TIMESTAMP,
    totalpeopleinvolved INTEGER,
    latitude DOUBLE,
    longitude DOUBLE
)
""")

db_conn.execute("""
CREATE TABLE IF NOT EXISTS arrests (
    case_number VARCHAR,
    arrest_date TIMESTAMP,
    totalpeopleinvolved INTEGER
)
""")

# Helper function to parse date
def parse_date(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")

# Fetch data from API only if missing in DuckDB
def fetch_and_store(api_id, table_name, date_field, year, month, day):
    client = Socrata("data.cityofgainesville.org", "tdAo9J2AL2LD9JFQh7jdIHScm")

    # Check if data already exists for the given date
    existing = db_conn.execute(f"""
        SELECT COUNT(*) FROM {table_name} 
        WHERE YEAR({date_field}) = ? 
        AND MONTH({date_field}) = ? 
        AND DAY({date_field}) = ?
    """, (year, month, day)).fetchone()[0]

    if existing > 0:
        # print(f"Data for {table_name} already exists. Skipping API fetch.")
        return

    # Fetch from API
    offset = 0
    limit = 10000
    all_data = []
    
    while True:
        results = client.get(api_id, limit=limit, offset=offset)
        if not results:
            break
        all_data += results
        offset += limit

    # Filter and store in DuckDB
    filtered_data = []
    for record in all_data:
        date_str = record.get(date_field)
        if not date_str:
            continue
        dt = parse_date(date_str)
        if dt.year == year and dt.month == month and dt.day == day:
            filtered_data.append(record)

    if filtered_data:
        if table_name == "arrests":
            db_conn.executemany(f"""
                INSERT INTO {table_name} VALUES (?, ?, ?)
            """, [
                (r.get("case_number"), r.get(date_field), int(r.get("totalpeopleinvolved", 1)))
                for r in filtered_data
            ])
            # print(f"Stored {len(filtered_data)} records in {table_name}.")
        else:
            db_conn.executemany(f"""
                INSERT INTO {table_name} VALUES (?, ?, ?, ?, ?)
            """, [
                ((r.get("case_number") or r.get("id")), r.get(date_field), int(r.get("totalpeopleinvolved", 1)), float(r.get("longitude", 0)), float(r.get("latitude", 0)))
                for r in filtered_data
            ])
            # print(f"Stored {len(filtered_data)} records in {table_name}.")

# Query incidents from DuckDB
def get_incidents(year, month, day):
    crashes = db_conn.execute("""
        SELECT * FROM traffic_crashes 
        WHERE YEAR(accident_date) = ? 
        AND MONTH(accident_date) = ? 
        AND DAY(accident_date) = ?
    """, (year, month, day)).fetchall()

    crimes = db_conn.execute("""
        SELECT * FROM crime_records 
        WHERE YEAR(offense_date) = ? 
        AND MONTH(offense_date) = ? 
        AND DAY(offense_date) = ?
    """, (year, month, day)).fetchall()

    arrests = db_conn.execute("""
        SELECT * FROM arrests 
        WHERE YEAR(arrest_date) = ? 
        AND MONTH(arrest_date) = ? 
        AND DAY(arrest_date) = ?
    """, (year, month, day)).fetchall()

    return crashes, crimes, arrests

# Find highest total people involved in crashes
def findHighestTotalPeople(crashes):
    max_people = max(crashes, key=lambda x: x[2], default=None)
    return [c for c in crashes if c[2] == max_people[2]] if max_people else []

# Compare distance to find related incidents
def compareDistance(x, data):
    return [record for record in data if geodesic(x, (record[4], record[3])).km < 1]

# Count cases and people involved
def update_case_counts(records, case_counts):
    # print("----------------------------------------")
    # print("RECORDS: ", records)
    for record in records:
        case_number = record[0]  # case_number is the first column in each table
        people_involved = record[2] if len(record) > 2 else 1  # Default to 1 if missing

        if case_number:
            case_counts[case_number] = case_counts.get(case_number, 0) + people_involved

    return case_counts

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    parser.add_argument("--day", type=int, required=True)
    args = parser.parse_args()

    # Fetch and store data
    fetch_and_store("iecn-3sxx", "traffic_crashes", "accident_date", args.year, args.month, args.day)
    fetch_and_store("gvua-xt9q", "crime_records", "offense_date", args.year, args.month, args.day)
    fetch_and_store("aum6-79zv", "arrests", "arrest_date", args.year, args.month, args.day)

    # Retrieve stored data
    crashes, crimes, arrests = get_incidents(args.year, args.month, args.day)

    if not crashes:
        # print("No traffic crashes found.")
        exit()

    # Find highest total people involved
    highest_cases = findHighestTotalPeople(crashes)
    longitude = highest_cases[0][3]
    latitude = highest_cases[0][4]
    x = (latitude, longitude)

    # Find related crimes and crashes near location
    filtered_crimes_loc = compareDistance(x, crimes)
    filtered_crashes_loc = compareDistance(x, crashes)

    # Create a set of case numbers from filtered crimes and crashes
    filtered_case_numbers = set(crime[0] for crime in filtered_crimes_loc) | set(crash[0] for crash in filtered_crashes_loc)

    # Filter arrests based on the case numbers
    filtered_arrests = [arrest for arrest in arrests if arrest[0] in filtered_case_numbers]

    # Count cases
    case_counts = {}
    case_counts = update_case_counts(filtered_crimes_loc, case_counts)
    case_counts = update_case_counts(filtered_crashes_loc, case_counts)
    case_counts = update_case_counts(filtered_arrests, case_counts)

    # Sort and print results
    sorted_items = sorted(case_counts.items(), key=lambda x: x[1], reverse=True)
    for case_number, people_count in sorted_items:
        print(f"{people_count}\t{case_number}")
