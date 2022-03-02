import keyword
from re import A
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException  
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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

    checkbox_xpath_with_id_placeholder = "//input[@type='checkbox'][@id='%s']"
    number_input_min_xpath_with_placeholders = "//div[contains(@class, 'ant-input-number')]//input[@id='%s'][@name='range-min']"
    number_input_max_xpath_with_placeholders = "//div[contains(@class, 'ant-input-number')]//input[@id='%s'][@name='range-max']"


    public_data_column_selector =".container > .row:nth-last-child(2) > div:last-child"
    number_input_selector = ".ant-input-number input"

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

    # ui - check configuration + checkboxes
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
                time.sleep(self.scroll_pause_time_seconds)
                
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

    # ui - test input boxes minimum/maximum limits
    def test_public_query_parameter_form_number_input_limits(self):
        self.navigate_to_public()

        # retrieve the fields json object from public endpoint
        fields_json = self.get_json_data(self.fields_path).json()

        # gather all number fields (both extra- and non-extra-properties)
        # under one dictionary to simplify looping
        
        # - get and structure extra_properties
        number_extra_props = {}
        extra_properties_json = fields_json["extra_properties"]
        for extra_prop_Key in extra_properties_json:
            if "type" in extra_properties_json[extra_prop_Key] and extra_properties_json[extra_prop_Key]["type"] == "number":
                number_extra_props[extra_prop_Key] = extra_properties_json[extra_prop_Key]

        # - remove extra_properties from original json dict
        fields_json.pop("extra_properties")

        # - get and structure non-extra-properties
        number_non_extra_props = {}
        non_extra_properties_json = fields_json
        for non_extra_prop_Key in non_extra_properties_json:
            if "type" in non_extra_properties_json[non_extra_prop_Key] and non_extra_properties_json[non_extra_prop_Key]["type"] == "number":
                number_non_extra_props[non_extra_prop_Key] = non_extra_properties_json[non_extra_prop_Key]

        # - combine the fields
        all_number_fields = {**number_extra_props, **number_non_extra_props}


        # - get all number inputs
        for key in all_number_fields.keys():
            minimum = None
            maximum = None
            bin_size = None

            if "minimum" in all_number_fields[key]:
                minimum = float(all_number_fields[key]["minimum"])
            if "maximum" in all_number_fields[key]:
                maximum = float(all_number_fields[key]["maximum"])
            if "bin_size" in all_number_fields[key]:
                bin_size = float(all_number_fields[key]["bin_size"])


            # retrieve html elements corresponding with this iteration's element key
            min_number_input = self.driver.find_element_by_xpath(self.number_input_min_xpath_with_placeholders % key)
            max_number_input = self.driver.find_element_by_xpath(self.number_input_max_xpath_with_placeholders % key)
            corresponding_checkbox = self.driver.find_element_by_xpath(self.checkbox_xpath_with_id_placeholder % key)

            # scroll to the element
            self.scroll_shim(corresponding_checkbox)
            time.sleep(self.scroll_pause_time_seconds)

            # enable query parameter
            corresponding_checkbox.click()

            # get the input into view
            self.scroll_shim(min_number_input)
            time.sleep(self.scroll_pause_time_seconds)
            
            # navigate up and down the input's range randomly
            rand=random.randrange(0,10,1)
            for i in range(rand):
                # obtain the input element's value before sending it a DOWN key
                pre_key_value=float(min_number_input.get_attribute('value'))
                
                min_number_input.send_keys(Keys.ARROW_DOWN)
                time.sleep(self.scroll_pause_time_seconds / 10)

                # obtain the input element's value after sending it a DOWN key
                value = float(min_number_input.get_attribute('value'))

                # compare with minimum value if available
                if minimum!= None:
                    assert value >= minimum
                    if value == minimum:
                        break
                # if sent key didnt change the value without triggering an exeception
                # (i.e if a minimum was hit), exit the loop
                if pre_key_value == value:
                    break

            rand=random.randrange(0,10,1)
            for i in range(rand):
                # obtain the input element's value before sending it an UP key
                pre_key_value=float(max_number_input.get_attribute('value'))
                
                max_number_input.send_keys(Keys.ARROW_UP)
                time.sleep(self.scroll_pause_time_seconds / 10)
                
                # obtain the input element's value after sending it an UP key
                value = float(max_number_input.get_attribute('value'))

                # compare with maximum value if available
                if maximum != None:
                    assert value <= maximum
                    if value == maximum:
                        break
                # if sent key didnt change the value without triggering an exeception
                # (i.e if a maximum was hit), exit the loop
                if pre_key_value == value:
                    break

            # ensure cannot set value greater than max or less than min
            if minimum != None:
                min_number_input.clear()
                attempted_less_than_min_value = str(float(minimum) - 1)
                
                min_number_input.send_keys(attempted_less_than_min_value)
                time.sleep(self.scroll_pause_time_seconds / 10)
                
                # unfocus
                self.driver.execute_script("document.activeElement.blur()", None)
                time.sleep(self.scroll_pause_time_seconds / 10)

                min_post_key_value=float(min_number_input.get_attribute('value'))

                assert min_post_key_value == minimum
            
            if maximum != None:
                max_number_input.clear()
                attempted_greater_than_max_value = str(float(maximum) + 1)
                
                max_number_input.send_keys(attempted_greater_than_max_value)
                time.sleep(self.scroll_pause_time_seconds / 10)
                
                # unfocus
                self.driver.execute_script("document.activeElement.blur()", None)
                time.sleep(self.scroll_pause_time_seconds / 10)

                max_post_key_value=float(max_number_input.get_attribute('value'))

                assert max_post_key_value == maximum

            if bin_size != None:
                min_number_input.clear()
                min_attempted_less_than_bin_size_max_value = 0
                min_number_input.send_keys(str(min_attempted_less_than_bin_size_max_value))

                max_number_input.clear()
                max_attempted_less_than_bin_size_max_value = bin_size - 1
                max_number_input.send_keys(str(max_attempted_less_than_bin_size_max_value))

                time.sleep(self.scroll_pause_time_seconds / 10)
                
                # unfocus
                self.driver.execute_script("document.activeElement.blur()", None)
                time.sleep(self.scroll_pause_time_seconds / 10)

                min_post_key_value=float(min_number_input.get_attribute('value'))
                max_post_key_value=float(max_number_input.get_attribute('value'))

                assert (max_post_key_value - min_post_key_value) == bin_size

            # re-disable query parameter
            corresponding_checkbox.click()



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
                            assert "count" in json_body or "message" in json_body

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
        