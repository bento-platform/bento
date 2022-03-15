from selenium import webdriver

import os
import unittest
import time
import requests
import pytest

@pytest.mark.usefixtures("setup")
class TestDrsApi():
    drs_path = "/api/drs"

    def test_access_api_search_json_objects(self):
        # GET
        response = requests.get(f'{self.bentov2_url}{self.drs_path}/search?fuzzy_name=.json', verify=False)
        
        assert response.status_code == 200
        assert response.json() != None and len(response.json()) >= 0

