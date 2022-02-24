from selenium.common.exceptions import NoSuchElementException        
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import pytest

@pytest.mark.usefixtures("setup")
class TestPublic():
    data_button_xpath = "//*[@id='root']/section/section/main/div/div[5]/div/button"
    spinner_xpath = "//*[@id='root']/section/section/main/div/div[5]/div/div"

    def test_navigate_to_public(self):
        self.navigate_to_public()
        

    def test_get_public_data(self):
        self.navigate_to_public()

        # time.sleep(self.pause_time_seconds)

        # wait for and obtain the get data button element
        get_data_button_element = WebDriverWait(self.driver, self.max_wait_time_seconds).until(
            EC.presence_of_element_located((By.XPATH, self.data_button_xpath))
        )

        # scroll down to the button element        
        self.scroll_shim(get_data_button_element)
        time.sleep(self.pause_time_seconds)

        # re-retrieve the button, wait for it to be clickable and then click
        get_data_button_element = WebDriverWait(self.driver, self.max_wait_time_seconds).until(
            EC.element_to_be_clickable((By.XPATH, self.data_button_xpath)))

        # click 'get data' button
        get_data_button_element.click()

        # retrieve and wait for spinner to disappear
        spinner_element = WebDriverWait(self.driver, self.max_wait_time_seconds).until(
            EC.presence_of_element_located((By.XPATH, self.spinner_xpath))
        )

        assert WebDriverWait(self.driver, self.max_wait_time_seconds).until(
            lambda redundant_driver: spinner_element.is_displayed() == False)

        


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
        