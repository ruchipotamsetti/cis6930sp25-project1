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

def getTrafficCrashes(year, month, day):
    client = Socrata("data.cityofgainesville.org", None)
    limit = 10000
    offset = 0
    traffic_crashes = []
    while True:
       results = client.get("iecn-3sxx", limit=limit, offset=offset)
       if not results:
           break
       traffic_crashes += results
       offset += limit
    traffic_crashes = filter_by_date(traffic_crashes, "accident_date", year, month, day)
    return traffic_crashes

def getCrimeRecords(year, month, day):
    client = Socrata("data.cityofgainesville.org", None)
    limit = 1000
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
    client = Socrata("data.cityofgainesville.org", None)
    
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


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int)
    parser.add_argument("--month", type=int)
    parser.add_argument("--day", type=int)
    args = parser.parse_args()

    traffic_crashes = getTrafficCrashes(args.year, args.month, args.day)

    crime_records = getCrimeRecords(args.year, args.month, args.day)

    arrests = getArrests(args.year, args.month, args.day)

    highest_cases = findHighestTotalPeople(traffic_crashes)
    longitude = highest_cases[0]['longitude']
    latitude = highest_cases[0]['latitude']
    x = (latitude, longitude)

    filtered_crimes_loc = compareDistance(x, crime_records)

    filtered_crashes_loc = compareDistance(x, traffic_crashes)

    case_counts = {}
    case_counts = update_case_counts(filtered_crimes_loc, case_counts)
    case_counts = update_case_counts(filtered_crashes_loc, case_counts)
    case_counts = update_case_counts(arrests, case_counts)

    sorted_items = sorted(case_counts.items(), key=lambda x: x[1], reverse=True)
    for case_number, people_count in sorted_items:
        print(f"{people_count}\t{case_number}")
