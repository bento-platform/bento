from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException        

import os
import unittest
import time
import requests
import pytest

@pytest.mark.usefixtures("setup")
class TestPublic():
    data_button_xpath = "//*[@id='root']/section/section/main/div/div[5]/div/button"

    def test_navigate_to_public(self):
        self.navigate_to_public()
        

    def test_get_public_data(self):
        self.navigate_to_public()

        time.sleep(self.pause_time_seconds)

        # obtain the get data button element
        assert self.check_exists_by_xpath(self.data_button_xpath)
        
        get_data_button_element = self.driver.find_element_by_xpath(self.data_button_xpath)

        # scroll down to the button element        
        self.scroll_shim(get_data_button_element)

        time.sleep(self.pause_time_seconds)

        # click get data
        get_data_button_element.click()
        time.sleep(2)

        


    # helpful utilities
    def navigate_to_public(self):
        # navigate to bentov2 public page
        self.driver.get(self.bentov2_public_url)
        time.sleep(self.pause_time_seconds)

        # verify successful navigation
        assert "Bento-Public" in self.driver.title
    
    def scroll_shim(self, object):
        # obtain element coordinates
        x = object.location['x']
        y = object.location['y']
        
        # construct javascript execution code
        scroll_by_coord = 'window.scrollTo(%s,%s);' % (
            x,
            y
        )
        
        # execute javascriptcode
        self.driver.execute_script(scroll_by_coord)

    def check_exists_by_xpath(self, xpath):
        try:
            self.driver.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return False
        return True
        