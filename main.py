import pandas as pd
from sodapy import Socrata
import requests
import json
import argparse
from datetime import datetime
from geopy.distance import geodesic
from collections import Counter

def parse_date(date):
    dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
    return dt.year, dt.month, dt.day

def filter_by_date(records, key, year, month, day):
    return [record for record in records if parse_date(record[key]) == (year, month, day)]

def getData(api, date_key, year, month, day): 
    client = Socrata("data.cityofgainesville.org", "tdAo9J2AL2LD9JFQh7jdIHScm")
    
    # Ensure month and day are two-digit formatted
    month = str(month).zfill(2)
    day = str(day).zfill(2)
    
    # Construct date string in the required format (YYYY-MM-DD)
    date_str = f"{year}-{month}-{day}T00:00:00.000"
    
    # Query data using SoQL
    results = client.get(
        api,
        where=f"{date_key} >= '{date_str}' AND {date_key} < '{year}-{month}-{int(day) + 1}T00:00:00.000'",
        limit=10  # Fetch up to 10 records
    )
    
    # print("----------------------------------")
    # print(len(results))
    # print("----------------------------------")
    
    return results  # Return the results if needed

def getCrimeRecords(year, month, day):
    client = Socrata("data.cityofgainesville.org", "tdAo9J2AL2LD9JFQh7jdIHScm")
    limit = 10000
    offset = 0
    crime_records = []
    while True:
        res = client.get("gvua-xt9q", limit=limit, offset=offset)
        if not res:
            break
        crime_records += res
        offset += limit
    crime_records = filter_by_date(crime_records, "offense_date", year, month, day)
    return crime_records


def getArrests(year, month, day):
    client = Socrata("data.cityofgainesville.org", "tdAo9J2AL2LD9JFQh7jdIHScm")
    limit = 10000
    offset = 0
    arrests = []
    while True:
        res = client.get("aum6-79zv", limit=limit, offset=offset)
        if not res:
            break
        arrests += res
        offset += limit
    arrests = filter_by_date(arrests, "arrest_date", year, month, day)
    return arrests
    
def findHighestTotalPeople(data):
    max_people = max(int(entry["totalpeopleinvolved"]) for entry in data)
    highest_cases = [entry for entry in data if int(entry["totalpeopleinvolved"]) == max_people]
    return highest_cases

def compareDistance(x, data):
    filtered_crimes = []
    for record in data:
        lat = record["latitude"]
        long = record["longitude"]
        coordinates = (lat, long)
        case_number = record.get("case_number") or record.get("id")
        # print("DISTANCE: ", case_number," ", geodesic(x, coordinates).km)
        if geodesic(x, coordinates).km <=1:
            filtered_crimes.append(record)
    return filtered_crimes

def update_case_counts(records, case_counts):
    for record in records:
        case_number = record.get("case_number") or record.get("id")
        people_involved = record.get("totalpeopleinvolved", 1)  # Default to 1 if not present

        if case_number:
            case_counts[case_number] = case_counts.get(case_number, 0) + int(people_involved)

    return case_counts

def create_case_people_dict(traffic_crashes, data):
    case_people_dict = {}

    # Convert traffic_crashes into a dictionary for quick lookup
    crash_dict = {crash['case_number']: crash['totalpeopleinvolved'] for crash in traffic_crashes}  # case_number -> totalpeopleinvolved

    for record in data:
        if "id" in record:
            case_number = record['id'] 
        else:
            case_number = record['case_number']
        
         # Check if totalpeopleinvolved exists in the record
        if "totalpeopleinvolved" in record and record["totalpeopleinvolved"] is not None:
            total_people = record["totalpeopleinvolved"]
            case_people_dict[case_number] = int(total_people)
        elif case_number in crash_dict:
            case_people_dict[case_number] = int(crash_dict[case_number])
        # If neither condition is met, we don't add the case_number to the dictionary

    # print(case_people_dict)
    return case_people_dict

def add_location_to_arrests(traffic_crashes, arrests):
    # Create a dictionary from traffic_crashes for quick lookup
    crash_locations = {}
    for crash in traffic_crashes:
        case_number = crash.get('case_number')
        lat = crash.get('latitude') 
        lon = crash.get('longitude') 
        if case_number and lat is not None and lon is not None:
            crash_locations[case_number] = (lat, lon)
    
    # Filter and update arrests with location data where possible
    matched_arrests = []
    for arrest in arrests:
        case_number = arrest.get('case_number')
        if case_number in crash_locations:
            # print("CASE NUMBER: ", case_number)
            arrest['latitude'], arrest['longitude'] = crash_locations[case_number]
            matched_arrests.append(arrest)
    return matched_arrests

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int)
    parser.add_argument("--month", type=int)
    parser.add_argument("--day", type=int)
    args = parser.parse_args()

    # print("TRAFFIC CRASHES: ")
    traffic_crashes = getData("iecn-3sxx", "accident_date", args.year, args.month, args.day)
    if len(traffic_crashes)==0:
        exit
    # print("CRIME RESPONSES: ")
    crime_responses = getData("gvua-xt9q", "offense_date", args.year, args.month, args.day)
    # print("ARRESTS: ")
    arrests = getData("aum6-79zv", "arrest_date", args.year, args.month, args.day)

    highest_cases = findHighestTotalPeople(traffic_crashes)
    # print("HIGHEST: ", json.dumps(highest_cases, indent=4))

    longitude = highest_cases[0]['longitude']
    latitude = highest_cases[0]['latitude']
    x = (latitude, longitude)

    # print("CRIME RECORDS:")
    filtered_crimes_loc = compareDistance(x, crime_responses)

    # print("TRAFFIC CRASHES:")
    filtered_crashes_loc = compareDistance(x, traffic_crashes)

    total_records = filtered_crashes_loc + filtered_crimes_loc

    case_counts = create_case_people_dict(traffic_crashes, total_records)

    sorted_items = sorted(case_counts.items(), key=lambda x: x[1], reverse=True)
    for case_number, people_count in sorted_items:
        print(f"{people_count}\t{case_number}")

    