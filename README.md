# **cis6930sp25 -- Project 1 **

**Name:** Ruchita Potamsetti

---

## **Assignment Description**
This script fetches and processes crime records from the given API or a local file. It takes command line parameters like offset and limit to filter the number of records needed. Then from the filtered records relevant fields are extracted and are seperated by a thorn (`þ`) character before printing to STDOUT. Fields that have multiple entries are seperated by commas and the fields with null or empty entries are left blank.

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
    ├── test_fetching_data.py     # Tests related to downloading data from API.
    ├── test_output_format.py     # Tests to verify extraction of relevant fields and filtering.
    └── test_filtering_data.py    # Tests to verify the tab-separated output format.
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
- **`getDataFromApi(url)`** :
  - Fetches JSON data from the given API URL.
  - Parameters:
    - url (str): The API endpoint to fetch data from.
  - Returns: A list of JSON objects (crime records) if successful, otherwise an empty list.
- **`getDataFromFile(filepath)`** :
  - Reads incident data from a local JSON file.
  - Parameters:
     - filepath (str): The path to the JSON file.
  - Returns: A list of JSON objects (crime records) if successful, otherwise an empty list.
- **`formatValues(value)`** :
  - Formats the field values as required. If a field has multiple entries it is seperated by commas. If a field has null or empty entries it is considered as blank.
  - Parameters:
     - value: The value to format (can be a string, list, or None).
  - Returns: str: A formatted string. If the value is a list, it joins elements with commas. If the value is None, it returns an empty string.
- **`processData(crime_records, offset, limit)`** 
  - Loops through the received crime records applying offset and/or limit filtering, extracts relevant fields, and formats the output using a thorn separator.
  - Parameters: crime_records (list):
     - The list of crime records (JSON objects).
     - offset (int): The number of records to skip before processing.
     - limit (int): The number of records to return.
  - Returns: list: A list of formatted strings, where fields are separated by the thorn (þ) character.

---

## **Bugs and Assumptions**
- If both the API url and file are provided in the command line as arguments then it would fetch data from the API.
- The script makes the assumption that proper JSON is always returned by API responses.
- In order to retrieve data from a URL, an active internet connection is required.

---

