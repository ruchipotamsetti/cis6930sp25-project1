import pandas as pd
from sodapy import Socrata
import requests
import json
import argparse
from datetime import datetime
from geopy.distance import geodesic
from collections import Counter

# def compare_and_count(list1, list2, field1, field2):
#     # Extract values from the first list
#     values1 = [d[field1] for d in list1 if field1 in d]
    
#     # Extract values from the second list
#     values2 = [d[field2] for d in list2 if field2 in d]
    
#     # Count occurrences
#     count1 = Counter(values1)
#     count2 = Counter(values2)
    
#     # Find common values and their counts
#     common = set(count1.keys()) & set(count2.keys())
#     for value in common:
#         print(f"Value '{value}' occurs {count1[value]} times in list1 and {count2[value]} times in list2")
    
#     # Find values unique to list1
#     only_in_list1 = set(count1.keys()) - set(count2.keys())
#     for value in only_in_list1:
#         print(f"Value '{value}' occurs {count1[value]} times in list1 but not in list2")
    
#     # Find values unique to list2
#     only_in_list2 = set(count2.keys()) - set(count1.keys())
#     for value in only_in_list2:
#         print(f"Value '{value}' occurs {count2[value]} times in list2 but not in list1")




def parse_date(date):
    dt = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%f")
    return dt.year, dt.month, dt.day

def filter_by_date(records, key, year, month, day):
    return [record for record in records if parse_date(record[key]) == (year, month, day)]

def getTrafficCrashes(year, month, day):
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
    traffic_crashes = filter_by_date(traffic_crashes, "accident_date", year, month, day)
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
    # print(f"Highest totalpeopleinvolved: {max_people}")
    # print("Cases with highest totalpeopleinvolved:")
    # print(json.dumps(highest_cases, indent=4))
    # for case in highest_cases:
    #     print(case)
    return highest_cases

def compareDistance(x, data):
    filtered_crimes = []
    for record in data:
        lat = record["latitude"]
        long = record["longitude"]
        coordinates = (lat, long)
        # print("DISTANCE: ", geodesic(x, coordinates).km)
        if geodesic(x, coordinates).km <1:
            filtered_crimes.append(record)
    return filtered_crimes

def update_case_counts(records, case_counts):
    """
    Updates a dictionary with case numbers and the number of people involved.

    Args:
        records (list of dict): List of records containing 'case_number' and optionally 'totalpeopleinvolved'.
        case_counts (dict): Dictionary to store and update {case_number: total_people}.

    Returns:
        dict: Updated case_counts dictionary.
    """
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
    # # print(json.dumps(traffic_crashes, indent=4))
    # print("Length traffic crashes: ", len(traffic_crashes))

    crime_records = getCrimeRecords(args.year, args.month, args.day)
    # print(json.dumps(crime_records, indent=4))
    # print("Length crime records: ", len(crime_records))

    arrests = getArrests(args.year, args.month, args.day)
    # print(json.dumps(arrests, indent=4))
    # print("Length crime records: ", len(arrests))

    highest_cases = findHighestTotalPeople(traffic_crashes)
    longitude = highest_cases[0]['longitude']
    latitude = highest_cases[0]['latitude']
    # print(longitude, " ", latitude)
    x = (latitude, longitude)

    # print("--------------------------------------------------")
    filtered_crimes_loc = compareDistance(x, crime_records)
    # print("filtered_crimes_by_location: ", len(filtered_crimes_loc))
    # print(json.dumps(filtered_crimes_loc, indent=4))

    # print("--------------------------------------------------")
    filtered_crashes_loc = compareDistance(x, traffic_crashes)
    # print("filtered_crashes_by_location: ", len(filtered_crashes_loc))    

    
    # compare_and_count(crime_records, arrests, 'id', 'case_number')
    # print("--------------------------------------------------")
    # compare_and_count(traffic_crashes, arrests, 'case_number', 'case_number')

    # print("---------------------------------------------------")

    case_counts = {}
    case_counts = update_case_counts(filtered_crimes_loc, case_counts)
    case_counts = update_case_counts(filtered_crashes_loc, case_counts)
    case_counts = update_case_counts(arrests, case_counts)

    # print(case_counts)

    sorted_items = sorted(case_counts.items(), key=lambda x: x[1], reverse=True)
    for case_number, people_count in sorted_items:
        print(f"{people_count}\t{case_number}")