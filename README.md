# **cis6930sp25 -- Project 1 **

**Name:** Ruchita Potamsetti

---

## **Assignment Description**
This projects aim is to find a chain of incidents that occured on the same day. So this script first fetches traffic crashes, crime responses and arrests from the api(https://data.cityofgainesville.org/), filters them according to the command line arguments provided (year, month, day). Then finds the incident in traffic crashes that has the most people involved and then computes other incident that occured within 1km of it. Finally, prints these incident's total people involved and case number separated by a tab.

---

## **Project Structure** 

```plaintext
cis6930sp25-project1/
├── COLLABORATORS.md              # A markdown file describing collaborations and inspirations taken from other websites.
├── Pipfile                       # Defines the dependencies and virtual environment for the project (used with pipenv).
├── README.md                     # Project description and instructions.
├── main.py                       # Main Python script that contains the core functionality of the project.
├── pyproject.toml                # Configuration file for the project, used by pipenv.
├── Project1_demo.gif             # Demo video
└── .github/workflows          
    ├── pytest.yaml               # Configuration file for running tests using GitHub Actions (CI).
└── tests/                        # Directory containing all test files.
    ├── test_fetching_data.py     # Tests related to fetching data from API.
    ├── test_output_format.py     # Tests to verify tab-separated output format and order of output.
    └── test_filtering_data.py    # Tests to verify the x, identify incident within 1km, remove duplicates.
```

---

## **To Install**
To install the necessary dependencies using `pipenv`, run:
```sh
pipenv install -e .
```
This will create a virtual environment and install all required packages.

---

## **To Run**
Execute the program using:
```sh
pipenv run python main.py --year 2024 --month 12 --day 12
```

---

## **Example Output**
```sh
5       224018560
4       224018592
3       224018581
3       224018555
2       224018578
2       224018577
2       224018570
2       224018566
2       224018565
2       224018557
2       224018556
2       224018552
1       224018583
```

---

## **To Test**
After installing, use the command below to execute the pytests:
```sh
pipenv run python -m pytest -v
```

---

### **Demo**
![]()
---

## **Features and Functions**

### **`main.py`**
- **`getData(api, date_key, year, month, day)`** :
  - Fetches data from the `data.cityofgainesville.org` API using SoQL, filtering by the given date.
  - Parameters:
    - api (str): The dataset API identifier.
    - date_key (str): The field name in the dataset that represents the date.
    - year (int): The year of the records to retrieve.
    - month (int): The month of the records to retrieve.
    - day (int): The day of the records to retrieve.
  - Returns: list: A list of JSON objects representing the records filtered by date.
- **`findHighestTotalPeople(data)`** :
  - Finds the traffic crash records with the highest number of people involved.
  - Parameters:
     - data (list): A list of traffic crash records (JSON objects).
  - Returns: list: A list of JSON objects representing the crashes with the highest number of people involved.
- **`compareDistance(x, data)`** :
  - Filters incidents that occurred within a 1 km radius of a given location.
  - Parameters:
     - x (tuple): A tuple (latitude, longitude) representing the reference incident location.
     - data (list): A list of JSON objects representing incidents.
  - Returns: list: A list of incidents (JSON objects) that are within 1 km of the given location.
- **`removeDuplicates(traffic_crashes, data)`** 
  - Removes duplicate records before appending new records to the list of traffic crashes.
  - Parameters: crime_records (list):
     - traffic_crashes (list): A list of traffic crash records (JSON objects).
     - data (list): A list of new records (JSON objects) that need to be checked for duplication. 
  - Returns: list: A combined list of unique traffic crash records.
- **`add_total_people_and_sort(data)`** 
  - Ensures all records have a totalpeopleinvolved field, assigns a default value of 1 if missing, and sorts the records in descending order of totalpeopleinvolved and case_number.
  - Parameters: crime_records (list):
     - data (list): A list of JSON objects representing incidents.
  - Returns: list: A sorted list of incidents with missing values handled.
---

## **Bugs and Assumptions**
- If both the API url and file are provided in the command line as arguments then it would fetch data from the API.
- The script makes the assumption that proper JSON is always returned by API responses.
- In order to retrieve data from a URL, an active internet connection is required.
- Since crime_responses do not have totalpeopleinvolved value, default value of 1 is assumed.

---

