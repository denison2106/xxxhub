from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.utils import ChromeType
from extension import proxies
import time
import requests
import re
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

options = {
'proxy': {
    'http': 'http://M7MYoO:14FXo78cYu@46.8.107.231:3000',
    'https': 'https://M7MYoO:14FXo78cYu@46.8.107.231:3000',
    'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
    }
}

def recaptcha():
    navigator = webdriver.Chrome(service=Service(ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()), seleniumwire_options=options)
    link = f'https://2ip.ru'
    navigator.get(link)
    time.sleep(80)


def cse_tok(cx, proxy):
    data = dict()
    r = requests.get(f'https://cse.google.com/cse.js?hpg=1&cx={cx}', proxies=proxy['http'])
    soup = BeautifulSoup(r.text, 'lxml')
    # cse_token = re.search('cse_token": "(.*)"', r.text, re.MULTILINE)
    data['cse_token'] = re.search('cse_token": "(.*)"', r.text).group(1)
    data['cselibv'] = re.search('cselibVersion": "(.*)"', r.text).group(1)
    return data


def cse_pars(tag, cx, proxy):
    cse_token = cse_tok(cx, proxy)
    data = cse_token
    query = f'{tag[1]}'
    as_oq = 'porn+porno'
    hl = 'ru'
    gl = 'us'
    cse_token = data['cse_token']
    cselibv = data['cselibv']
    searchtype = 'image'
    url = f'https://cse.google.com/cse/element/v1?rsz=20&num=20&hl={hl}&source=gcsc&gss=.com&cselibv={cselibv}' \
          f'&searchtype={searchtype}&cx={cx}&q={query}&safe=off&cse_tok={cse_token}&lr=&cr=&gl={gl}&filter=0' \
          f'&sort=&as_oq={as_oq}&as_sitesearch=&exp=csqr,cc,4861326&imgsz=medium&cseclient=hosted-page-client' \
          f'&callback=google.search.cse.api1359'
    r = requests.get(url, proxies=proxy['http'])
    url_solved = f'https://cse.google.com/cse?cx={cx}#gsc.tab=0&gsc.q={query}'
    # print(url_solved.replace(" ", "%20"))
    # print(r.text)

    if re.search('error":\{(.+)\}', r.text, re.MULTILINE | re.DOTALL):
        if int(re.search('code":(.+),', r.text, re.MULTILINE | re.DOTALL).group(1)) == 429:
            print('Ip Banned')
        # recaptcha(query, cx, proxy)
        print(r.text)
    else:
        if re.search('results": \[(.+)\]', r.text, re.MULTILINE|re.DOTALL):
            arr = re.search('results": \[(.+)\]', r.text, re.MULTILINE|re.DOTALL).group(1)
            res = f'[{arr}]'
            # print(res)
            # return rasparse(json.loads(res), tag)
        else:
            # update_tag(tag[0], '', '', '', 2)
            return 'Skip'


proxy = dict()
proxy['ip'] = '46.8.107.231'
proxy['port'] = '3000'
proxy['user'] = 'M7MYoO'
proxy['password'] = '14FXo78cYu'
proxy['http'] = {'https': f"http://{proxy['user']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"}

cx = 'f158c7f38d4ef4f06'

cse_pars('sex', cx, proxy)