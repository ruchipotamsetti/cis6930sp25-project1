import pandas as pd
from sodapy import Socrata
import requests
import json
import argparse
from datetime import datetime
from geopy.distance import geodesic
from collections import Counter
import sys

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
        limit=50000  # Fetch up to 10 records
    )
    
    # print("----------------------------------")
    # print(len(results))
    # print("----------------------------------")
    
    return results  # Return the results if needed

def getTrafficCrashes():
    client = Socrata("data.cityofgainesville.org", "tdAo9J2AL2LD9JFQh7jdIHScm")
    limit = 10000
    offset = 0
    traffic_crashes = []
    while True:
       results = client.get("iecn-3sxx", limit=limit, offset=offset)
       if not results:
           break
       traffic_crashes += results
       offset += limit
    # traffic_crashes = filter_by_date(traffic_crashes, "accident_date", year, month, day)
    return traffic_crashes

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
        if geodesic(x, coordinates).km <1:
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
        # print("CASE NUMBER: ", case_number)
        
         # Check if totalpeopleinvolved exists in the record
        if "totalpeopleinvolved" in record and record["totalpeopleinvolved"] is not None:
            total_people = record["totalpeopleinvolved"]
            case_people_dict[case_number] = int(total_people)
        else:
            case_people_dict[case_number] = 1
        # elif case_number in crash_dict:
        #     case_people_dict[case_number] = int(crash_dict[case_number])
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

# def ensure_total_people_and_sort(data):
#     for record in data:
#         if "totalpeopleinvolved" not in record:
#             record["totalpeopleinvolved"] = 1  # Default value if missing
    
#     # Function to extract the correct date and convert it into a sortable format
#     def extract_date(record):
#         date_str = record.get("offense_date") or record.get("accident_date")
#         return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f") if date_str else datetime.min

#     # Sorting: First by totalpeopleinvolved, then by extracted date
#     # data.sort(key=lambda record: (int(record["totalpeopleinvolved"]), extract_date(record)))
#     data.sort(key=lambda record: (-int(record["totalpeopleinvolved"]), -extract_date(record)))

#     # Printing in the required format
#     for record in data:
#         case_number = record.get("case_number") or record.get("id")
#         print(f"{record['totalpeopleinvolved']}\t{case_number}")

def ensure_total_people_and_sort(data):
    for record in data:
        if "totalpeopleinvolved" not in record:
            record["totalpeopleinvolved"] = 1  # Default value if missing
    
    # Function to extract the correct date and convert it into a sortable format
    def extract_date(record):
        date_str = record.get("report_date") or record.get("accident_date")
        return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f") if date_str else datetime.min

    # Sorting:
    # - Descending by totalpeopleinvolved (-int(record["totalpeopleinvolved"]))
    # - Descending by date (later dates first, so negate timestamp)
    data.sort(key=lambda record: (-int(record["totalpeopleinvolved"]), -extract_date(record).timestamp()))

    # Printing in the required format
    for record in data:
        date = record.get("report_date") or record.get("accident_date")
        case_number = record.get("case_number") or record.get("id")
        print(f"{record['totalpeopleinvolved']}\t{case_number}")

def join_and_deduplicate(traffic_crashes, data):
    existing_casenumbers = {crash.get("case_number") for crash in traffic_crashes}
    new_traffic_crashes = traffic_crashes[:]
    for record in data:
        casenumber = record.get("case_number") or record.get("id")#Use .get() to handle missing 'casenumber' gracefully.
        if casenumber not in existing_casenumbers and record not in new_traffic_crashes: #Check if already present
          new_traffic_crashes.append(record)
          existing_casenumbers.add(casenumber)

    return new_traffic_crashes

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int)
    parser.add_argument("--month", type=int)
    parser.add_argument("--day", type=int)
    args = parser.parse_args()


    traffic_crashes = getData("iecn-3sxx", "accident_date", args.year, args.month, args.day)
    if not traffic_crashes:
        sys.exit()
    
    crime_responses = getData("gvua-xt9q", "report_date", args.year, args.month, args.day)
   
    highest_cases = findHighestTotalPeople(traffic_crashes)

    longitude = highest_cases[0]['longitude']
    latitude = highest_cases[0]['latitude']
    x = (latitude, longitude)
    
    filtered_crimes_loc = compareDistance(x, crime_responses)
    # print("LENGTH CRIMES: ", len(filtered_crimes_loc))
    # print("CRIMES: ", json.dumps(filtered_crimes_loc, indent=4))
    
    filtered_crashes_loc = compareDistance(x, traffic_crashes)

    # total_records = filtered_crashes_loc + filtered_crimes_loc
    all_records = join_and_deduplicate(filtered_crashes_loc, filtered_crimes_loc)

    ensure_total_people_and_sort(all_records)


    