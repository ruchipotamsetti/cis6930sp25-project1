from sodapy import Socrata
import json
import argparse
from datetime import datetime
from geopy.distance import geodesic
import sys

# fetching data from https://data.cityofgainesville.org/ using SoQL -> fitering by date
def getData(api, date_key, year, month, day): 
    client = Socrata("data.cityofgainesville.org", "tdAo9J2AL2LD9JFQh7jdIHScm")
    
    # ensure month and day are two-digit formatted
    month = str(month).zfill(2)
    day = str(day).zfill(2)
    
    # Construct date string in the required format (YYYY-MM-DD)
    date_str = f"{year}-{month}-{day}T00:00:00.000"
    
    # querying data using SoQL
    results = client.get(
        api,
        where=f"{date_key} >= '{date_str}' AND {date_key} < '{year}-{month}-{int(day) + 1}T00:00:00.000'",
        limit=50000 
    )
    
    return results  # return the filtered records

# find traffic crash records that has the highest people involved
def findHighestTotalPeople(data):
    max_people = max(int(entry["totalpeopleinvolved"]) for entry in data)
    highest_cases = [entry for entry in data if int(entry["totalpeopleinvolved"]) == max_people]
    return highest_cases

#compute the distance of other incidents from x(incident with highest people involved) 
def compareDistance(x, data):
    filtered_crimes = []
    for record in data:
        lat = record["latitude"]
        long = record["longitude"]
        coordinates = (lat, long)
        if geodesic(x, coordinates).km <1:
            filtered_crimes.append(record)
    return filtered_crimes

# this function ensures that there are no duplicates in the filtered records before appending
def removeDuplicates(traffic_crashes, data):
    existing_casenumbers = {crash.get("case_number") for crash in traffic_crashes}
    new_traffic_crashes = traffic_crashes[:]
    for record in data:
        casenumber = record.get("case_number") or record.get("id")
        if casenumber not in existing_casenumbers and record not in new_traffic_crashes: #Check if already present
          new_traffic_crashes.append(record)
          existing_casenumbers.add(casenumber)

    return new_traffic_crashes

# this function adds totalpeopleinvolved if not present and sorts in descending order of totalpeopleinvolved and case_number
def add_total_people_and_sort(data):
    for record in data:
        if "totalpeopleinvolved" not in record:
            record["totalpeopleinvolved"] = 1  # Default value if missing

    data.sort(key=lambda record: (-int(record["totalpeopleinvolved"]), -int(record.get("case_number") or record.get("id"))), reverse=False)

    for record in data:
        case_number = record.get("case_number") or record.get("id")
        print(f"{record['totalpeopleinvolved']}\t{case_number}")
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int)
    parser.add_argument("--month", type=int)
    parser.add_argument("--day", type=int)
    args = parser.parse_args()


    traffic_crashes = getData("iecn-3sxx", "accident_date", args.year, args.month, args.day)
    if not traffic_crashes: #exit if traffic crashes is empty
        sys.exit()
    
    #fetching traffic crashes, crime responses, and arrests
    crime_responses = getData("gvua-xt9q", "report_date", args.year, args.month, args.day)

    arrests = getData("aum6-79zv", "arrest_date", args.year, args.month, args.day)
   
   #finding traffic crash with the most people involved(x)
    highest_cases = findHighestTotalPeople(traffic_crashes)

    # extracting co-ordinates of x
    longitude = highest_cases[0]['longitude']
    latitude = highest_cases[0]['latitude']
    x = (latitude, longitude)
    
    # filtering remaining incidents based on distance(distance<1)
    filtered_crimes_by_distance = compareDistance(x, crime_responses)
    filtered_crashes_by_distance = compareDistance(x, traffic_crashes)

    #removing duplicates before appending
    all_filtered_records = removeDuplicates(filtered_crashes_by_distance, filtered_crimes_by_distance)

    #adding default value of 1 if totalpeopleinvolved is empty and sorting 
    add_total_people_and_sort(all_filtered_records)


    