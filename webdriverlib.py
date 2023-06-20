from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os

def get_chromium_location():
    potential_locations = [
        '/usr/bin/chromium-browser',
        '/snap/bin/chromium',
    ]
    for location in potential_locations:
        if os.path.isfile(location):
            return location
    raise FileNotFoundError("Cannot find chromium")

def get_text(url, xpath_to_wait = None):
    options = webdriver.ChromeOptions()
    options.headless = True
    options.binary_location = get_chromium_location()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--single-process')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument("--remote-debugging-port=9222"),
    # Adding argument to disable the AutomationControlled flag 
    options.add_argument("--disable-blink-features=AutomationControlled") 
    
    # Exclude the collection of enable-automation switches 
    options.add_experimental_option("excludeSwitches", ["enable-automation"]) 
    
    # Turn-off userAutomationExtension 
    options.add_experimental_option("useAutomationExtension", False) 
    driver_location = os.path.abspath(os.path.dirname(__file__)+'/bin/chromedriver')

    with webdriver.Chrome(executable_path=driver_location, options=options) as driver:
        driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"}) 
        driver.get(url)
        if xpath_to_wait:
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, xpath_to_wait)))
        return driver.page_source
