from selenium import webdriver

import os
import unittest
import time
import requests
import pytest

@pytest.mark.usefixtures("setup")
class TestKatsuApi():
    metadata_path = "/api/metadata"

    def test_access_api_experiment_tables(self):
        # GET
        response = requests.get(f'{self.bentov2_url}{self.metadata_path}/tables?data-type=experiment&format=json', verify=False)
        
        assert response.status_code == 200
        assert response.json() != None and len(response.json()) >= 0
