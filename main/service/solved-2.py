from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
from anticaptchaofficial.recaptchav2proxyless import *
from selenium.webdriver.support.wait import WebDriverWait
from twocaptcha import TwoCaptcha
import time
from extension import proxies

username = 'vhCepa'
password = 'zNRpbV0urv'
endpoint = '188.130.142.249'
port = '5500'

chrome_options = webdriver.ChromeOptions()
proxies_extension = proxies(username, password, endpoint, port)
chrome_options.add_extension(proxies_extension)
# chrome_options.add_argument("--headless=chrome")

navigator = webdriver.Chrome('E:/chromedriver.exe', options=chrome_options)

link = 'https://www.google.com/recaptcha/api2/demo'
navigator.get(link)

site_key = navigator.find_element(By.ID, 'recaptcha-demo').get_attribute('data-sitekey')

solver = TwoCaptcha('')
proxy = {
    'type': 'HTTPS',
    'uri': f"{username}:{password}@{endpoint}:{port}"
}
result = solver.recaptcha(sitekey=site_key, url=link, proxy=proxy)
res_captcha = result['code']

# solver = recaptchaV2Proxyless()
# solver.set_verbose(1)
# solver.set_key('5df1c6ed38216eb76b68fcc599109f1f')
# solver.set_website_url(link)
# solver.set_website_key(site_key)

# res_captcha = solver.solve_and_return_solution()
#
if res_captcha != 0:
    print(res_captcha)
    navigator.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{res_captcha}'")
    navigator.find_element(By.ID, 'recaptcha-demo-submit').click()
else:
    print(solver.err_string)

# WebDriverWait(navigator, 120).until(lambda x: x.find_element_by_css_selector('.recaptcha-success'))
time.sleep(60)