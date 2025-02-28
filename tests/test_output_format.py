import pytest
from main import ensure_total_people_and_sort

def test_output_format(capsys):
    sample_data = [
        {"case_number": "101", "totalpeopleinvolved": 3},
        {"case_number": "102", "totalpeopleinvolved": 2}
    ]

    ensure_total_people_and_sort(sample_data)
    captured = capsys.readouterr()

    expected_output = "3\t101\n2\t102\n"
    assert captured.out == expected_output
