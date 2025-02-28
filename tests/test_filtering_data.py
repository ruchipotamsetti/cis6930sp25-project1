import pytest
from main import findHighestTotalPeople, compareDistance, join_and_deduplicate, ensure_total_people_and_sort

def test_findHighestTotalPeople():
    sample_data = [
        {"case_number": "101", "totalpeopleinvolved": 2},
        {"case_number": "102", "totalpeopleinvolved": 5},
        {"case_number": "103", "totalpeopleinvolved": 5}
    ]
    highest = findHighestTotalPeople(sample_data)
    assert len(highest) == 2  # Two cases have max people involved
    assert highest[0]["totalpeopleinvolved"] == 5

def test_compareDistance():
    reference_location = (29.65163, -82.32482)  # Sample coordinates
    sample_data = [
        {"case_number": "101", "latitude": 29.652, "longitude": -82.325},
        {"case_number": "102", "latitude": 30.000, "longitude": -83.000}
    ]
    nearby = compareDistance(reference_location, sample_data)
    assert len(nearby) == 1  # Only the first case is within 1km

def test_join_and_deduplicate():
    dataset1 = [{"case_number": "101", "totalpeopleinvolved": 2}]
    dataset2 = [{"case_number": "101", "totalpeopleinvolved": 2}, {"case_number": "102", "totalpeopleinvolved": 3}]
    
    combined = join_and_deduplicate(dataset1, dataset2)
    assert len(combined) == 2  # Deduplicated correctly
    assert any(entry["case_number"] == "102" for entry in combined)

def test_ensure_total_people_and_sort():
    sample_data = [
        {"case_number": "101", "totalpeopleinvolved": 2},
        {"case_number": "102", "totalpeopleinvolved": 5},
        {"case_number": "103"}  # Missing totalpeopleinvolved
    ]
    
    sorted_data = ensure_total_people_and_sort(sample_data)
    assert sorted_data[0]["totalpeopleinvolved"] == 5  # Highest should be first
    assert sorted_data[-1]["totalpeopleinvolved"] == 1  # Defaulted to 1
