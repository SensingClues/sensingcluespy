"""Tests for the API-calls available in wildcat-api-python"""


# import os
# import pytest
# import unittest
# from unittest.mock import Mock, patch
#
#
# from sensingclues import api_calls
# from sensingclues.api_calls import SensingClues
# from dotenv import load_dotenv


# @patch('sensingclues.api_calls.SensingClues.login')
# def test_login(mock_get):
#     # Configure the mock to return a response with an OK status code.
#     mock_get.response.status_code = 200
#
#     load_dotenv()
#     username = os.getenv("USERNAME")
#     password = os.getenv('PASSWORD')
#     cat_api = SensingClues(username, password)
#
#     response = cat_api.login(username, password)
#     print(response)
#
#     assert response.status_code == 200, 'woah'

# class TestApi(unittest.TestCase):
#     # @classmethod
#     def set_up(self):
#         load_dotenv()
#         self.username = os.getenv("USERNAME")
#         self.password = os.getenv('PASSWORD')
#         self.cat_api = SensingClues(self.username, self.password)

# @mock.patch('mymodule.os.path')
# @mock.patch('mymodule.os')
# @pytest.mark.api_call

# def test_login(self):
#
#     self.set_up()
#     print(self.username)
#     response = self.cat_api.login(self.username, self.password)
#     self.assertEqual(response.status_code, 200)
