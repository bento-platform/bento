from selenium import webdriver

import os
import unittest
import time
import requests
import pytest

# helper functions
import common

@pytest.mark.usefixtures("setup")
class TestLogins():
    expectedTitle = "Sign in to bentov2"
    signInButtonXPath = "//*[@id='root']/section/main/main/div/div[2]/button"

    def test_login_access_admin_services(self):
        # credentials
        u1 = os.environ["BENTOV2_AUTH_TEST_USER"]
        p1 = os.environ["BENTOV2_AUTH_TEST_PASSWORD"]

        assert u1 != "" and p1 != ""
        
        # navigate to bentov2
        self.driver.get(self.bentov2_url)
        time.sleep(self.debug_pause_time_seconds)

        # click "Sign in" button
        self.driver.find_element_by_xpath(self.signInButtonXPath).click()
        time.sleep(self.debug_pause_time_seconds)

        # enter invalid credentials
        common.login(self.driver, u1, p1, self.expectedTitle)
        time.sleep(self.debug_pause_time_seconds)

        # verify successful login
        assert "Overview" in self.driver.title

        # navigate to admin services page
        # - move mouse over "admin" tab
        action = webdriver.ActionChains(self.driver)

        admin_tab = self.driver.find_element_by_xpath("//*[@id='root']/section/header/ul/li[8]/div")
        action.move_to_element(admin_tab)
        time.sleep(self.debug_pause_time_seconds)
        action.perform()
        time.sleep(self.debug_pause_time_seconds)

        services_subtab = self.driver.find_element_by_xpath("//*[@id='item_3$Menu']/li[1]/a")
        action.move_to_element(services_subtab)
        time.sleep(self.debug_pause_time_seconds)
        action.perform()
        time.sleep(self.debug_pause_time_seconds)
        services_subtab.click()
        time.sleep(self.debug_pause_time_seconds)

        # - verify services are available
        service_rows = self.driver.find_elements_by_xpath("//*[@id='root']/section/main/section/main/section/main/div[2]/div/div/div/div/div/table/tbody/tr")
        for row in service_rows:
            assert "HEALTHY" in row.text



