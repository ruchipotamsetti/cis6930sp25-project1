import pytest
from main import getData

def test_getData(mocker):
    mock_response = [{"case_number": "123", "totalpeopleinvolved": 3}]
    
    # Mock the Socrata client response
    mocker.patch("main.Socrata.get", return_value=mock_response)
    
    data = getData("iecn-3sxx", "accident_date", 2024, 2, 26)
    assert isinstance(data, list)
    assert len(data) > 0
    assert "case_number" in data[0]
    assert "totalpeopleinvolved" in data[0]
