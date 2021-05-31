from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import os
import unittest
import time
import requests
import pytest


# -- helper functions --
def login(driver, username, password):
    # Ensure we are on the login page
    assert "Sign in to bentov2" in driver.title

    # Retrieve credential input elements
    username_input = driver.find_elements_by_xpath("//*[@id='username']")[0]
    password_input = driver.find_elements_by_xpath("//*[@id='password']")[0]

    login_button = driver.find_elements_by_xpath("//*[@id='kc-login']")[0]

    # Enter credentials
    username_input.send_keys(username)
    password_input.send_keys(password)

    # Click login button
    login_button.click()
# -- - --


@pytest.mark.usefixtures("setup")
class TestLogins():
    
    def test_login_user(self):
        # credentials
        u1 = os.environ["BENTOV2_AUTH_TEST_USER"]
        p1 = os.environ["BENTOV2_AUTH_TEST_PASSWORD"]
        
        # Navigate to bentov2
        self.driver.get(self.bentov2_url)
        time.sleep(self.debug_pause_time_seconds)

        # Click "Sign in" button
        self.driver.find_element_by_xpath("//*[@id='root']/section/main/main/div/div[2]/button").click()
        time.sleep(self.debug_pause_time_seconds)

        # Enter invalid credentials
        login(self.driver, u1, p1)
        time.sleep(self.debug_pause_time_seconds)

        # verify successful login
        assert "Overview" in self.driver.title



    def test_login_bogus_user(self):
        # credentials
        fake_username = "nobody"
        fake_password = "jibberishPassword123$$$$"
        
        # Navigate to bentov2
        self.driver.get(self.bentov2_url)
        time.sleep(self.debug_pause_time_seconds)

        # Click "Sign in" button
        self.driver.find_element_by_xpath("//*[@id='root']/section/main/main/div/div[2]/button").click()
        time.sleep(self.debug_pause_time_seconds)

        # Enter invalid credentials
        login(self.driver, fake_username, fake_password)
        time.sleep(self.debug_pause_time_seconds)

        # verify invalid login
        assert "Invalid username or password." in self.driver.find_elements_by_xpath("//*[@id='kc-content-wrapper']/div[1]")[0].text

