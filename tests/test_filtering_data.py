from main import findHighestTotalPeople, compareDistance, removeDuplicates, add_total_people_and_sort

# testing if record with most people involved is correctly identified
def test_findHighestTotalPeople():
    sample_data = [
        {"case_number": "101", "totalpeopleinvolved": 2},
        {"case_number": "102", "totalpeopleinvolved": 5},
        {"case_number": "103", "totalpeopleinvolved": 5}
    ]
    highest = findHighestTotalPeople(sample_data)
    assert len(highest) == 2  # Two cases have max people involved
    assert highest[0]["totalpeopleinvolved"] == 5

# testing if only incidents within 1 km of x are indentified
def test_compareDistance():
    reference_location = (29.65163, -82.32482)  # Sample coordinates
    sample_data = [
        {"case_number": "101", "latitude": 29.652, "longitude": -82.325},
        {"case_number": "102", "latitude": 30.000, "longitude": -83.000}
    ] 
    nearby = compareDistance(reference_location, sample_data)
    assert len(nearby) == 1  # Only the first case is within 1km

# testing if duplicates are removed before appending
def test_remove_duplicates():
    dataset1 = [{"case_number": "101", "totalpeopleinvolved": 2}]
    dataset2 = [{"case_number": "101", "totalpeopleinvolved": 2}, {"case_number": "102", "totalpeopleinvolved": 3}]
    
    combined = removeDuplicates(dataset1, dataset2)
    assert len(combined) == 2  # Deduplicated correctly
    assert any(entry["case_number"] == "102" for entry in combined)

# testing adding default people involved and sorting
def test_add_total_people_and_sort():
    sample_data = [
        {"case_number": "101", "totalpeopleinvolved": 5},
        {"case_number": "102", "totalpeopleinvolved": 5},
        {"case_number": "103"}  # Missing totalpeopleinvolved
    ]
    
    sorted_data = add_total_people_and_sort(sample_data)
    assert sorted_data[0]["case_number"] == "102"  # Highest with larger case number should be first
    assert sorted_data[1]["case_number"] == "101" 
