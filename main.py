import pandas as pd
from sodapy import Socrata
import requests
import json
import argparse
from datetime import datetime

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
    # print(json.dump(traffic_crashes, indent=4))
    print("Before filtering length traffic crashes: ", len(traffic_crashes))
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
    # print(json.dump(crime_records, indent=4))
    print("Before filtering length crime records: ", len(crime_records))
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
    # print(json.dumps(arrests, indent=4))
    print("Before filtering length arrests: ", len(arrests))
    arrests = filter_by_date(arrests, "arrest_date", year, month, day)
    return arrests

if __name__ == "__main__":
    print("Hello World!")

    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int)
    parser.add_argument("--month", type=int)
    parser.add_argument("--day", type=int)
    args = parser.parse_args()

    traffic_crashes = getTrafficCrashes(args.year, args.month, args.day)
    # # print(json.dumps(traffic_crashes, indent=4))
    print("Length traffic crashes: ", len(traffic_crashes))

    crime_records = getCrimeRecords(args.year, args.month, args.day)
    # print(json.dumps(crime_records, indent=4))
    print("Length crime records: ", len(crime_records))

    arrests = getArrests(args.year, args.month, args.day)
    # print(json.dumps(arrests, indent=4))
    print("Length crime records: ", len(arrests))