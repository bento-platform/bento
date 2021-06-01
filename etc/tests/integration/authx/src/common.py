# Common test functions

def login(driver, username, password, expectedTitle):
    # Ensure we are on the login page
    assert expectedTitle in driver.title

    # Retrieve credential input elements
    username_input = driver.find_elements_by_xpath("//*[@id='username']")[0]
    password_input = driver.find_elements_by_xpath("//*[@id='password']")[0]

    login_button = driver.find_elements_by_xpath("//*[@id='kc-login']")[0]

    # Enter credentials
    username_input.send_keys(username)
    password_input.send_keys(password)

    # Click login button
    login_button.click()


def fix_padding(data):
    missing_padding = len(data) % 4
    if missing_padding:
        data += "=" * (4 - missing_padding)
    return data