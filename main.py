import pandas as pd
from sodapy import Socrata
import requests
import json
import argparse

def getTrafficCrashes():
    # res = requests.get("https://data.cityofgainesville.org/resource/iecn-3sxx.json?$limit=10000&$$app_token=tdAo9J2AL2LD9JFQh7jdIHScm") 
    # if res.status_code == 200:
    #     traffic_crashes = res.json()
    #     return traffic_crashes
    # else:
    #     print(f"Error: {res.status_code}")
    #     return []
    client = Socrata("data.cityofgainesville.org", None)

    limit = 10000
    offset = 0
    traffic_crashes = []
    while True:
       results = client.get("aum6-79zv", limit=limit, offset=offset)
       if not results:
           break
       traffic_crashes += results
       offset += limit
    return traffic_crashes



if __name__ == "__main__":
    print("Hello World!")
    # client = Socrata("data.cityofgainesville.org", None)
    # results = client.get("aum6-79zv", limit=70000)
    # results_df = pd.DataFrame.from_records(results)
    # print(results_df)

    traffic_crashes = getTrafficCrashes()
    # print(json.dumps(traffic_crashes, indent=4))
    print("Length: ", len(traffic_crashes))

    # parser = argparse.ArgumentParser()
    # parser.add_argument("--year", type=str)
    # parser.add_argument("--month", type=str)
    # parser.add_argument("--day", type=str)
    # args = parser.parse_args()

    # traffic_crashes = getTrafficCrashes(args.year, args.month, args.day)
    # print(traffic_crashes)