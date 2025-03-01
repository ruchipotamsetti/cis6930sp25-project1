from main import add_total_people_and_sort

#testing the sorting and format of output
def test_output_format(capsys):
    sample_data = [
    {
        "case_number": "223020088",
        "dhsmv_number": "26242219",
        "accident_date": "2023-12-20T23:51:57.000",
        "accident_hour_of_day": "23",
        "crash_minutes": "51",
        "accident_day_of_week": "Wednesday",
        "occurred_on": "US 441 (SW 13TH ST)",
        "intersecttype": "FOUR-WAY INTERSECTION",
        "at_from_intersection": "SW 2ND AVE",
        "totalpeopleinvolved": "6",
        "numberofbicyclesinvolved": "0",
        "numberofpedestriansinvolved": "0",
        "totalvehiclesinvolved": "3",
        "numberofmopedsinvolved": "0",
        "numberofmotorcylesinvolved": "0",
        "numberofbusesinvolved": "1",
        "totalfatalities": "0",
        "geox": "265486125",
        "geoy": "24298073",
        "longitude": "-82.32272",
        "latitude": "29.65198",
        "location": {
          "type": "Point",
          "coordinates": [-82.32272, 29.65198]
        },
        "city": "Gainesville",
        "state": "Florida",
        ":@computed_region_ecgy_hwrz": "1",
        ":@computed_region_e6r8_dw75": "13",
        ":@computed_region_u9vc_vmbc": "1",
        ":@computed_region_4rat_gsiv": "772",
        ":@computed_region_axii_i744": "4"
    },
    {
        "case_number": "223019953",
        "dhsmv_number": "26242188",
        "accident_date": "2023-12-18T16:21:32.000",
        "accident_hour_of_day": "16",
        "crash_minutes": "21",
        "accident_day_of_week": "Monday",
        "occurred_on": "SW 5TH ST",
        "at_street_address": "229",
        "intersecttype": "NOT AT INTERSECTION",
        "totalpeopleinvolved": "1",
        "numberofbicyclesinvolved": "0",
        "numberofpedestriansinvolved": "0",
        "totalvehiclesinvolved": "2",
        "numberofmopedsinvolved": "0",
        "numberofmotorcylesinvolved": "0",
        "numberofbusesinvolved": "0",
        "totalfatalities": "0",
        "geox": "265797425",
        "geoy": "24278338",
        "longitude": "-82.329288024",
        "latitude": "29.649533001",
        "location": {
          "type": "Point",
          "coordinates": [-82.32272, 29.65198]
        },
        "city": "Gainesville",
        "state": "Florida",
        ":@computed_region_ecgy_hwrz": "1",
        ":@computed_region_e6r8_dw75": "13",
        ":@computed_region_u9vc_vmbc": "1",
        ":@computed_region_4rat_gsiv": "772",
        ":@computed_region_axii_i744": "4"
    },
    {
        "case_number": "223019957",
        "dhsmv_number": "26242192",
        "accident_date": "2023-12-18T16:46:41.000",
        "accident_hour_of_day": "16",
        "crash_minutes": "46",
        "accident_day_of_week": "Monday",
        "occurred_on": "CR 329 (N MAIN ST)",
        "intersecttype": "FOUR-WAY INTERSECTION",
        "at_from_intersection": "SR 222 (NE 39TH AVE)",
        "totalpeopleinvolved": "2",
        "numberofbicyclesinvolved": "0",
        "numberofpedestriansinvolved": "0",
        "totalvehiclesinvolved": "2",
        "numberofmopedsinvolved": "0",
        "numberofmotorcylesinvolved": "0",
        "numberofbusesinvolved": "0",
        "totalfatalities": "0",
        "geox": "266093325",
        "geoy": "25698056",
        "longitude": "-82.32272",
        "latitude": "29.65198",
        "location": {
          "type": "Point",
          "coordinates": [-82.32272, 29.65198]
        },
        "city": "Gainesville",
        "state": "Florida",
        ":@computed_region_ecgy_hwrz": "1",
        ":@computed_region_e6r8_dw75": "13",
        ":@computed_region_u9vc_vmbc": "1",
        ":@computed_region_4rat_gsiv": "772",
        ":@computed_region_axii_i744": "4"
    },
    ]

    add_total_people_and_sort(sample_data)
    captured = capsys.readouterr()

    expected_output = "6\t223020088\n2\t223019957\n1\t223019953\n" 
    assert captured.out == expected_output
