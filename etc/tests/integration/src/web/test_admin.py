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
        time.sleep(self.pause_time_seconds)

        # click "Sign in" button
        self.driver.find_element_by_xpath(self.signInButtonXPath).click()
        time.sleep(self.pause_time_seconds)

        # enter invalid credentials
        common.login(self.driver, u1, p1, self.expectedTitle)
        time.sleep(self.pause_time_seconds)

        # verify successful login
        assert "Overview" in self.driver.title

        # navigate to admin services page
        # - move mouse over "admin" tab
        action = webdriver.ActionChains(self.driver)

        admin_tab = self.driver.find_element_by_xpath("//*[@id='root']/section/header/ul/li[8]/div")
        action.move_to_element(admin_tab)
        time.sleep(self.pause_time_seconds)
        action.perform()
        time.sleep(self.pause_time_seconds)

        services_subtab = self.driver.find_element_by_xpath("//*[@id='item_3$Menu']/li[1]/a")
        action.move_to_element(services_subtab)
        time.sleep(self.pause_time_seconds)
        action.perform()
        time.sleep(self.pause_time_seconds)
        services_subtab.click()
        time.sleep(self.pause_time_seconds)

        # - verify services are available
        service_rows = self.driver.find_elements_by_xpath("//*[@id='root']/section/main/section/main/section/main/div[2]/div/div/div/div/div/table/tbody/tr")
        for row in service_rows:
            assert "HEALTHY" in row.text



    def test_login_access_drop_box_files(self):
        # credentials
        u1 = os.environ["BENTOV2_AUTH_TEST_USER"]
        p1 = os.environ["BENTOV2_AUTH_TEST_PASSWORD"]

        dropbox_project_dir = os.environ["BENTOV2_DROP_BOX_VOL_DIR"]

        assert u1 != "" and p1 != "" and dropbox_project_dir != ""

        # navigate to bentov2
        self.driver.get(self.bentov2_url)
        time.sleep(self.pause_time_seconds)

        # click "Sign in" button
        self.driver.find_element_by_xpath(self.signInButtonXPath).click()
        time.sleep(self.pause_time_seconds)

        # enter invalid credentials
        common.login(self.driver, u1, p1, self.expectedTitle)
        time.sleep(self.pause_time_seconds)

        # verify successful login
        assert "Overview" in self.driver.title

        # navigate to admin services page        
        # - move mouse over "admin" tab
        action = webdriver.ActionChains(self.driver)

        admin_tab = self.driver.find_element_by_xpath("//*[@id='root']/section/header/ul/li[8]/div")
        action.move_to_element(admin_tab)
        time.sleep(self.pause_time_seconds)
        action.perform()
        time.sleep(self.pause_time_seconds)

        # - move to data manager subtab
        datamanager_tab = self.driver.find_element_by_xpath("//*[@id='item_3$Menu']/li[2]/a")
        time.sleep(self.pause_time_seconds)
        action.move_to_element(datamanager_tab)
        time.sleep(self.pause_time_seconds)
        time.sleep(self.pause_time_seconds)
        action.perform()
        time.sleep(self.pause_time_seconds)
        time.sleep(self.pause_time_seconds)
        datamanager_tab.click()
        time.sleep(self.pause_time_seconds)

        # - move to files
        files_tab = self.driver.find_element_by_xpath("//*[@id='root']/section/main/section/main/div/div[2]/ul/li[4]/a")
        time.sleep(self.pause_time_seconds)
        files_tab.click()
        time.sleep(self.pause_time_seconds)

        # - verify files
        chord_drop_box = self.driver.find_element_by_xpath("//*[@id='root']/section/main/section/main/section/main/div[2]/div/ul/li/span[2]")
        time.sleep(self.pause_time_seconds)
        assert "chord_drop_box" in chord_drop_box.text

        # add a temporary test file
        project_abs_dir = self.project_root_abs_path
        temp_filename = "temp.txt"
        temp_filepath = f'{project_abs_dir}/{dropbox_project_dir}/{temp_filename}'
        with open(temp_filepath, 'w') as f:
            f.write('Create a new text file!')

        # refresh the page
        self.driver.refresh()

        time.sleep(self.pause_time_seconds)
        time.sleep(self.pause_time_seconds)

        # check if that temporary file is available

        # - (assume UI "folder" is already open)
        # chord_drop_box = self.driver.find_element_by_xpath("//*[@id='root']/section/main/section/main/section/main/div[2]/div/ul/li/span[2]")
        # time.sleep(self.pause_time_seconds)
        # # - "open" the folder
        # chord_drop_box.click()
        # time.sleep(self.pause_time_seconds)

        # - get the files
        chord_drop_box_files = self.driver.find_elements_by_xpath("//*[@id='root']/section/main/section/main/section/main/div[2]/div/ul/li/ul/li")
        time.sleep(self.pause_time_seconds)

        temp_file_exists = False
        for file_row in chord_drop_box_files:
            if temp_filename in file_row.text:
                temp_file_exists = True
                break

        assert temp_file_exists

        # delete temp file
        os.remove(temp_filepath)
