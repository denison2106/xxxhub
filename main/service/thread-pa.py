from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from extension import proxies
import time
from selenium.webdriver.common.by import By


def recaptcha():
    chrome_options = webdriver.ChromeOptions()
    proxies_extension = proxies('gFRKCO', 'OP13iimKcj', '45.11.20.3', '5500')
    chrome_options.add_extension(proxies_extension)
    chrome_options.add_argument(f"--proxy-server=45.89.19.100:16592")
    # chrome_options.add_argument("--headless=chrome")

    # navigator = webdriver.Chrome('E:/chromedriver.exe')
    navigator = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()), options=chrome_options)
    link = f'https://2ip.ru'
    navigator.get(link)
    time.sleep(80)



proxy = dict()
proxy['ip'] = '45.11.20.3'
proxy['port'] = '5500'
proxy['user'] = 'gFRKCO'
proxy['password'] = 'OP13iimKcj'
proxy['http'] = {'https': f"http://{proxy['user']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"}

recaptcha()