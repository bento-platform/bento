from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException       
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import requests
import pytest
import random

@pytest.mark.usefixtures("setup")
class TestPublic():

    overview_path = "/overview"
    fields_path = "/fields"
    config_path = "/config"
    katsu_path = "/katsu"

    data_button_xpath = "//*[@id='root']/section/section/main/div/div[5]/div/button"
    spinner_xpath = "//*[@id='root']/section/section/main/div/div[5]/div/div"
    chart_col_xpath = "//*[@id='root']/section/section/main/div/div[2]/div/div[1]/div"
    query_parameter_row_xpath ="//*[@id='root']/section/section/main/div/div[4]/div[1]/div/div"
    checkbox_xpath = "//input[@type='checkbox']"

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

    # TODO: ui - check configuration + checkboxes
    def test_public_query_parameter_form_checkbox_limits(self):
        self.navigate_to_public()

        # retrieve the fields json object from public endpoint
        config_json = self.get_json_data(self.config_path).json()

        # ensure we got what we needed
        assert "maxQueryParameters" in config_json
        max_qp = config_json["maxQueryParameters"]
        assert max_qp > 0

        # verify the checkboxes
        checkbox_count = 0
        # - get all checkboxes
        all_checkboxes = self.driver.find_elements_by_xpath(self.checkbox_xpath)
        # - randomize the list order
        random.shuffle(all_checkboxes)
        # - loop over the now-random list of checkboxes
        for checkbox in all_checkboxes:
            try:
                # get the checkbox into view
                self.scroll_shim(checkbox)
                time.sleep(0.25)
                
                # click on the checkbox
                checkbox.click()

                # increase the number of checked checkboxes count
                checkbox_count += 1
            except ElementClickInterceptedException:
                # expect the click to fail (be "intercepted")
                # if the max number of query parameters has been reached
                # and pass on this exception
                if checkbox_count >= max_qp:
                    pass
                else:
                    raise ElementClickInterceptedException



    # endpoint tests
    def test_can_retrieve_public_overview(self):
        # ping overview
        overview_response = self.get_json_data(self.overview_path)
        assert overview_response

    def test_can_retrieve_public_fields(self):
        # ping fields
        fields_response = self.get_json_data(self.fields_path)
        assert fields_response
    
    def test_can_retrieve_public_config(self):
        # ping config
        config_response = self.get_json_data(self.config_path)
        assert config_response
        
    def test_security_queryable_parameters(self):
        # retrieve the fields json object from public endpoint
        fields_json = self.get_json_data(self.fields_path).json()

        # gather all queryable fields (both extra- and non-extra-properties)
        # under one dictionary to simplify looping
        
        # - get and structure extra_properties
        extra_properties_json = fields_json["extra_properties"]
        for extra_prop_Key in extra_properties_json:
            extra_properties_json[extra_prop_Key]["is_extra_property_key"] = True

        # - remove extra_properties from original json dict
        fields_json.pop("extra_properties")

        # - get and structure non-extra-properties
        non_extra_properties_json = fields_json
        for non_extra_prop_Key in non_extra_properties_json:
            non_extra_properties_json[non_extra_prop_Key]["is_extra_property_key"] = False

        # - concatenate both dicts together to make one
        all_json = {**non_extra_properties_json, **extra_properties_json}
        
        # loop over properly-structured json
        for key in all_json:
            # obtain important parameters to construct POST body
            value_json = all_json[key]
            qp_type = value_json["type"]
            qp_is_extra_property_key = value_json["is_extra_property_key"]

            # generate random value
            qp_value = "giberish" if qp_type == "string" else 0

            # for number types, default is to expect a range,
            # so provide range min/max and ensure the difference
            # between the two is at least the bin-size
            qp_range_min = 0 if qp_type == "number" else None
            qp_range_max = value_json["bin_size"] if qp_type == "number" else None
            
            # setup json data
            data =[{
                "key": key,
                "type": qp_type,
                "value": qp_value,
                "is_extra_property_key": qp_is_extra_property_key,
                "rangeMax": qp_range_max,
                "rangeMin": qp_range_min
            }]

            # ensure this json value has fields we need
            if data != []:

                # expect different response from public data endpoints depending
                # on whether this variable can or cannot be queried for
                if "queryable" in value_json:
                    qp_queryable = value_json["queryable"]

                    # if item is queryable, ensure it is available on the dashboard
                    # by checking if the item was given a row with the item's title
                    # and thus if the the item's title is present in the concatenated
                    # string containing each element's title
                    if bool(qp_queryable):
                        
                        supposed_valid_query_response = requests.post(f'{self.bentov2_public_url}{self.katsu_path}', json=data, verify=False)
            
                        assert supposed_valid_query_response.status_code == 200

                        json_body = supposed_valid_query_response.json()
                        assert json_body != None

                        if json_body != {}:
                            assert "count" in json_body

                    else:
                        supposed_invalid_query_response = requests.post(f'{self.bentov2_public_url}{self.katsu_path}', json=data, verify=False)
            
                        assert supposed_invalid_query_response.status_code == 400
                        assert supposed_invalid_query_response.json() != None

                else: # "queryable" not in value_json
                    # default is to reject this query
                    supposed_invalid_query_response = requests.post(f'{self.bentov2_public_url}{self.katsu_path}', json=data, verify=False)
        
                    assert supposed_invalid_query_response.status_code == 400
                    assert supposed_invalid_query_response.json() != None



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
        