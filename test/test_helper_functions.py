import pandas as pd
import numpy as np

import unittest
from unittest.mock import patch

import helper_functions
import constants


def generate_mock_df():
    df = pd.DataFrame(
        {'DATE': pd.date_range('2022-01-01', periods=20).tolist(),
         'countriesAndTerritories': 'Austria',
         'cases': range(100, 200, 5),
         'deaths': range(10, 30, 1)
         }
    )
    return df


class TestGetDataAsDfFromUrl(unittest.TestCase):

    def setUp(self):
        self.data = constants.DUMMY_DATA

    @patch('helper_functions.get_data_from_url')
    def test_json_normalisation(self, get_data_from_url_mock):
        get_data_from_url_mock.return_value = self.data
        df_actual = pd.DataFrame({
         "dateRep": ["18/07/2022", "17/07/2022"],
         "day": [18, 17],
         "month": ["07", "07"],
         "year": [2022, 2022],
         "cases": [11862, 8362],
         "deaths": [5, 8],
         "countriesAndTerritories": ["Austria", "Austria"],
         "geoId": ["AT", "AT"],
         "countryterritoryCode": ["AUT", "AUT"],
         "popData2020": ["8901064", "8901064"],
         "continentExp": ["Europe", "Europe"]
        })
        df_expected = helper_functions.get_data_as_df_from_url(url='abc',
                                                               normalising_key='records',
                                                               convert_to_datetime=False)
        self.assertTrue(df_actual.equals(df_expected))


class TestGetLastWeekSum(unittest.TestCase):

    def setUp(self):
        self.df = generate_mock_df()

    def test_get_last_week_sum_computation(self):
        actual_total_weekly_cases = 165+170+175+180+185+190+195
        actual_total_weekly_deaths = 23+24+25+26+27+28+29
        total_percentage = 1
        weekly_expected = helper_functions.get_last_week_stats(self.df)
        self.assertEqual(actual_total_weekly_cases, weekly_expected.iloc[0]['cases'])
        self.assertEqual(actual_total_weekly_deaths, weekly_expected.iloc[0]['deaths'])
        self.assertEqual(total_percentage, weekly_expected.iloc[0]['%total_EU_weekly_cases'])
        self.assertEqual(total_percentage, weekly_expected.iloc[0]['%total_EU_weekly_deaths'])


class TestGetWeeklyChange(unittest.TestCase):
    def setUp(self):
        self.df = generate_mock_df()
        self.df_zeros = generate_mock_df()
        self.df_zeros['cases'] = 0
        self.df_nan = generate_mock_df()
        self.df_nan['cases'] = np.nan

    def test_get_weekly_change_computation(self):
        current_week_sum = 195+190+185+180+175+170+165
        last_week_sum = 160+155+150+145+140+135+130
        actual_weekly_change = (current_week_sum-last_week_sum)/last_week_sum*100
        weekly_change = helper_functions.get_weekly_change(self.df, 'cases')
        self.assertEqual(actual_weekly_change, weekly_change.iloc[0])

    def test_get_weekly_change_computation_with_nans(self):
        actual_weekly_change = 0
        weekly_change = helper_functions.get_weekly_change(self.df_nan, 'cases')
        self.assertEqual(actual_weekly_change, weekly_change.iloc[0])

    def test_get_weekly_change_computation_with_zeros(self):
        actual_weekly_change = 0
        weekly_change = helper_functions.get_weekly_change(self.df_zeros, 'cases')
        self.assertEqual(actual_weekly_change, weekly_change.iloc[0])


