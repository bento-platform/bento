from selenium.common.exceptions import NoSuchElementException        
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import requests
import pytest


@pytest.mark.usefixtures("setup")
class TestPublic():

    overview_path = "/overview"
    fields_path = "/fields"

    data_button_xpath = "//*[@id='root']/section/section/main/div/div[5]/div/button"
    spinner_xpath = "//*[@id='root']/section/section/main/div/div[5]/div/div"
    chart_col_xpath = "//*[@id='root']/section/section/main/div/div[2]/div/div[1]/div"
    query_parameter_row_xpath ="//*[@id='root']/section/section/main/div/div[4]/div[1]/div/div"

    public_data_column_selector =".container > .row:nth-last-child(2) > div:last-child"

    # browser tests
    def test_navigate_to_public(self):
        self.navigate_to_public()
        

    def test_get_public_data(self):
        self.navigate_to_public()

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

        # get data
        # wait for and obtain the data-containing column element (second-to-last row's last column)
        data_col_element = WebDriverWait(self.driver, self.max_wait_time_seconds).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, self.public_data_column_selector))
        )
        data_raw_text = data_col_element.text

        assert data_raw_text != "" and "count" in data_raw_text


    def test_presence_of_public_data_visualizations(self):
        self.navigate_to_public()

        # wait for presence of chart ( histogram or pie-chart )-containing bootstrap columns
        assert WebDriverWait(self.driver, self.max_wait_time_seconds).until(
            EC.presence_of_all_elements_located((By.XPATH, self.chart_col_xpath))
        )

    def test_presence_of_public_query_parameter_form(self):
        self.navigate_to_public()

        # retrieve the fields json object from public endpoint
        fields_json = self.get_json_data(self.fields_path).json()
        
        # wait for presence query-parameter-containing bootstrap rows
        all_query_parameter_rows = WebDriverWait(self.driver, self.max_wait_time_seconds).until(
            EC.presence_of_all_elements_located((By.XPATH, self.query_parameter_row_xpath))
        )
        assert all_query_parameter_rows

        # retrieve the raw text within each of the bootstrap rows
        all_qp_row_texts =  [x.text for x in all_query_parameter_rows]

        # for ease-of-comparisson, concatenate all text values together
        concatenated_qp_row_texts = ', '.join(all_qp_row_texts)

        # validate that all publicly-queryable fields have a form available to them
        for value_json in fields_json.values():
            # ensure this json value has fields we need
            if "title" in value_json:
                qp_title = value_json["title"]
                
                if "queryable" in value_json:
                    qp_queryable = value_json["queryable"]

                    # if item is queryable, ensure it is available on the dashboard
                    # by checking if the item was given a row with the item's title
                    # and thus if the the item's title is present in the concatenated
                    # string containing each element's title
                    if bool(qp_queryable):
                        assert qp_title in concatenated_qp_row_texts
                    else:
                        assert qp_title not in concatenated_qp_row_texts
                else: # "queryable" not in value_json
                    assert qp_title not in concatenated_qp_row_texts



    # endpoint tests
    def test_can_retrieve_public_overview(self):
        # ping overview
        overview_response = self.get_json_data(self.overview_path)
        assert overview_response

    def test_can_retrieve_public_fields(self):
        fields_response = self.get_json_data(self.fields_path)
        assert fields_response
        


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

    def get_json_data(self, path):
        # ping fields
        response = requests.get(f'{self.bentov2_public_url}{path}', verify=False)
        
        # validate response
        assert response.status_code == 200
        assert response.json()

        return response
        