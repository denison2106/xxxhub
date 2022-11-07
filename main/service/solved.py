# Import libraries and objects
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import time
import json


# The API messages sending directly to the plugin
# For example for the anti-captcha.com API key init which is required for the plugin work
# Works only on the normal HTML web page
# https://antcpt.com/blank.html in our case
# Won't work on pages like about:blank etc
def acp_api_send_request(driver, message_type, data={}):
    message = {
		# this receiver has to be always set as antiCaptchaPlugin
        'receiver': 'antiCaptchaPlugin',
        # request type, for example setOptions
        'type': message_type,
        # merge with additional data
        **data
    }
    # run JS code in the web page context
    # preceicely we send a standard window.postMessage method
    return driver.execute_script("""
    return window.postMessage({});
    """.format(json.dumps(message)))


# Init the chrome options object for connection the extension
options = webdriver.ChromeOptions()
# A full path to CRX or ZIP or XPI file which was downloaded earlier
options.add_extension('E:/anticaptcha-plugin_v0.63.crx')

# Run the browser (Chrome WebDriver) with passing the full path to the downloaded WebDriver file
browser = webdriver.Chrome('E:/chromedriver.exe', options=options)

# Go to the empty page for setting the API key through the plugin API request
browser.get('https://antcpt.com/blank.html')

# Setting up the anti-captcha.com API key
# replace YOUR-ANTI-CAPTCHA-API-KEY to your actual API key, which you can get from here:
# https://anti-captcha.com/clients/settings/apisetup
acp_api_send_request(
    browser,
    'setOptions',
    {'options': {'antiCaptchaApiKey': '5df1c6ed38216eb76b68fcc599109f1f'}}
)

# 3 seconds pause
time.sleep(3)

# Go to the test form with reCAPTCHA 2
browser.get('https://antcpt.com/rus/information/demo-form/recaptcha-2.html')

# Test input
browser.find_element_by_name('demo_text').send_keys('Test input')

# Most important part: we wait upto 120 seconds until the AntiCaptcha plugin indicator with antigate_solver class
# gets the solved class, which means that the captcha was successfully solved
WebDriverWait(browser, 120).until(lambda x: x.find_element_by_css_selector('.antigate_solver.solved'))

# Sending form
browser.find_element_by_css_selector('input[type=submit]').click()