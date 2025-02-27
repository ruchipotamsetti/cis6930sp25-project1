import duckdb
import pytest
from datetime import datetime
from main import get_incidents, findHighestTotalPeople, compareDistance, update_case_counts

@pytest.fixture(scope="module")
def setup_db():
    conn = duckdb.connect("incidents_test.duckdb")
    
    conn.execute("""
    CREATE TABLE traffic_crashes (
        case_number VARCHAR,
        accident_date TIMESTAMP,
        totalpeopleinvolved INTEGER,
        longitude DOUBLE,
        latitude DOUBLE
    )
    """)

    conn.execute("""
    CREATE TABLE crime_records (
        case_number VARCHAR,
        offense_date TIMESTAMP,
        totalpeopleinvolved INTEGER,
        latitude DOUBLE,
        longitude DOUBLE
    )
    """)

    conn.execute("""
    CREATE TABLE arrests (
        case_number VARCHAR,
        arrest_date TIMESTAMP,
        totalpeopleinvolved INTEGER
    )
    """)
    
    yield conn
    conn.close()

def test_findHighestTotalPeople():
    crashes = [
        ('TC1', datetime(2025, 2, 14), 3, -82.325, 29.651),
        ('TC2', datetime(2025, 2, 14), 10, -82.325, 29.651),
        ('TC3', datetime(2025, 2, 14), 10, -82.325, 29.651)
    ]
    result = findHighestTotalPeople(crashes)
    assert len(result) == 2
    assert result[0][2] == 10

def test_compareDistance():
    crashes = [
        ('TC1', datetime(2025, 2, 14), 3, -82.325, 29.651),
        ('TC2', datetime(2025, 2, 14), 5, -82.326, 29.652)
    ]
    reference_point = (29.651, -82.325)
    result = compareDistance(reference_point, crashes)
    assert len(result) == 2

def test_update_case_counts():
    crashes = [
        ('TC1', datetime(2025, 2, 14), 3, -82.325, 29.651),
        ('TC2', datetime(2025, 2, 14), 5, -82.326, 29.652)
    ]
    case_counts = update_case_counts(crashes, {})
    assert case_counts['TC1'] == 3
    assert case_counts['TC2'] == 5
