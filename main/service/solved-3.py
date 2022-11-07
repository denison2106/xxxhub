from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
from twocaptcha import TwoCaptcha
import time

navigator = webdriver.Chrome('E:/chromedriver.exe')
link = 'https://cse.google.com/cse?cx=f158c7f38d4ef4f06#gsc.tab=0&gsc.q=duygu'
navigator.get(link)
url_captcha = navigator.find_element(By.XPATH, "//*[@title='reCAPTCHA']").get_attribute('src')
site_key = re.search('k=(.*?)&', url_captcha).group(1)
print(site_key)
solver = TwoCaptcha('')
result = solver.recaptcha(sitekey=site_key, url=link)
res_captcha = result['code']

if res_captcha != 0:
    print(res_captcha)
    navigator.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{res_captcha}'")
    time.sleep(1)
    navigator.execute_script(f"___grecaptcha_cfg.clients[0].W.W.callback"
                             f"('{res_captcha}');")
else:
    # print(solver.err_string)
    quit()
time.sleep(120)
