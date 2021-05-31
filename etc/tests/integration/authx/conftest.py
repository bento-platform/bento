import os
import pytest
from selenium import webdriver
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options as ffOptions
from selenium.webdriver.chrome.options import Options as chOptions
import random

# Resources
# Firefox: http://chromedriver.chromium.org/
# Chrome: http://github.com/mozilla/geckodriver/releases

# to run, use `pytest -s -v -n=4` from this directory

@pytest.fixture(scope="session")
def setup(request):

    testname = os.environ.get('PYTEST_CURRENT_TEST').split(':')[-1].split(' ')[0]

    headless_mode = (os.environ["HEADLESS_MODE"] == 'True')
    
    if "login" in testname:
        driverenv = os.environ["DRIVER_ENV"]
        common_path = f'{os.getcwd()}/etc/tests/integration/authx'

        # Firefox
        fireFoxOptions = ffOptions()
        if headless_mode:
            fireFoxOptions.headless = True


        profile = webdriver.FirefoxProfile()
        profile.accept_untrusted_certs = True

        driver = webdriver.Firefox(firefox_profile=profile, executable_path=f'{common_path}/geckodriver', options=fireFoxOptions)


    
        # Randomly select (within reason) window dimensions and position
        width = random.randint(760,1900)
        height = random.randint(512,1024)
        x = random.randint(0, 500)
        y = random.randint(0, 500)

        driver.set_window_size(width, height)
        driver.set_window_position(x, y, windowHandle ='current')

    else:
        driver=None

    bentov2_url= os.environ["BENTOV2_PUBLIC_URL"]
    bentov2auth_url= os.environ["BENTOV2_AUTH_PUBLIC_URL"]

    session = request.node
    for item in session.items:
        cls = item.getparent(pytest.Class)
        setattr(cls.obj, "driver", driver)
        setattr(cls.obj, "debug_pause_time_seconds", 1)
        setattr(cls.obj, "bentov2_url", bentov2_url)
        setattr(cls.obj, "bentov2auth_url", bentov2auth_url)

    yield driver
    if driver != None:
        driver.close()