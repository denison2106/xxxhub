import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from extension import proxies
from twocaptcha import TwoCaptcha
import requests
import urllib.request
import time
import datetime
import re
import json
import numpy as np
import psycopg2
import multiprocessing
from bs4 import BeautifulSoup
from xxxhub import settings


conn = psycopg2.connect(
    dbname=settings.DATABASES['default']['NAME'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    host=settings.DATABASES['default']['HOST']
)

cursor = conn.cursor()


def get_tag(limit=100):
    cursor.execute(f"SELECT * FROM main_content WHERE status=0 ORDER BY id DESC LIMIT {limit}")
    return cursor.fetchall()


def update_tag(id, image, thumb, content, status):
    if status == 1:
        sql = f"UPDATE main_content SET date='{datetime.datetime.now()}', image = '{image}', thumb = '{thumb}', cse = '{content}', status = {status} WHERE id = '{id}'"
    else:
        sql = f"UPDATE main_content SET status = {status} WHERE id = '{id}'"
    cursor.execute(sql)
    conn.commit()


def recaptcha(query, cx, proxy):
    chrome_options = webdriver.ChromeOptions()
    proxies_extension = proxies(proxy['user'], proxy['password'], proxy['ip'], proxy['port'])
    # chrome_options.add_extension(proxies_extension)
    chrome_options.add_argument(f"--proxy-server={proxy['ip']}:{proxy['port']}")
    chrome_options.add_argument("--headless=chrome")

    # navigator = webdriver.Chrome('E:/chromedriver.exe')
    navigator = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    link = f'https://cse.google.com/cse?cx={cx}#gsc.tab=0&gsc.q={query}'
    navigator.get(link)
    url_captcha = navigator.find_element(By.XPATH, "//*[@title='reCAPTCHA']").get_attribute('src')
    site_key = re.search('k=(.*?)&', url_captcha).group(1)
    solver = TwoCaptcha('')
    proxy = {
        'type': 'HTTPS',
        'uri': f"{proxy['user']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"
    }
    result = solver.recaptcha(sitekey=site_key, url=link, proxy=proxy)
    res_captcha = result['code']

    if res_captcha != 0:
        try:
            navigator.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{res_captcha}'")
            time.sleep(1)
            navigator.execute_script(f"___grecaptcha_cfg.clients[0].Z.Z.callback('{res_captcha}');")
            time.sleep(10)
        except Exception as e:
            pass


def cse_tok(cx, proxy):
    data = dict()
    r = requests.get(f'https://cse.google.com/cse.js?hpg=1&cx={cx}', proxies=proxy['http'])
    soup = BeautifulSoup(r.text, 'lxml')
    # cse_token = re.search('cse_token": "(.*)"', r.text, re.MULTILINE)
    data['cse_token'] = re.search('cse_token": "(.*)"', r.text).group(1)
    data['cselibv'] = re.search('cselibVersion": "(.*)"', r.text).group(1)
    return data


def rasparse(arr, tag):
    ci = random.randint(1, 4)
    time.sleep(1)
    if len(arr) > 5:
        i = 1
        json = '{ "content": ['
        for row in arr:
            title = row['titleNoFormatting'].replace('\'', '').replace('"', '').replace('\\', '')
            image = row['unescapedUrl'].replace("'", "%27")
            thumb = row['tbLargeUrl'].replace("'", "%27")
            url = row['originalContextUrl'].replace("'", "%27")
            domain = re.match('.*\/\/(.*?)\/', url).group(1)
            # print(i, title, image, url)
            data = f'"title": "{title}", "image": "{image}", "thumb": "{thumb}", "url": "{url}", "domain": "{domain}"'
            json += ' {' + data + '},'
            if i == ci:
                con_image = image
                con_thumb = thumb
            i += 1
        json += '] }'
        content = json.replace(',]', ' ]')
        update_tag(tag[0], con_image, con_thumb, content, 1)
    else:
        content = 'Min Thumbs Skip'
        update_tag(tag[0], '', '',  '', 2)
    return content


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

    if re.search('error":\{(.+)\}', r.text, re.MULTILINE | re.DOTALL):
        recaptcha(query, cx, proxy)
        print('ReCaptcha')
    else:
        if re.search('results": \[(.+)\]', r.text, re.MULTILINE|re.DOTALL):
            arr = re.search('results": \[(.+)\]', r.text, re.MULTILINE|re.DOTALL).group(1)
            res = f'[{arr}]'
            # print(res)
            return rasparse(json.loads(res), tag)
        else:
            update_tag(tag[0], '', '', '', 2)
            return 'Skip'


def res(i, tag, cx, proxy):
    result = cse_pars(tag, cx, proxy)
    print(i, proxy['ip'], tag[1], result)


proxy_ip = [
    '188.130.185.124',
    '45.15.73.169',
    '109.248.205.8',
    '109.248.143.106',
    '185.181.245.68',
    '109.248.167.244',
    # '46.8.22.147',
    '46.8.223.200',
    # '188.130.128.189',
    '45.87.252.124',
    '46.8.222.24',
    '5.183.130.232',
    '109.248.143.114',
    '46.8.107.231',
    '46.8.17.180',
    '188.130.137.214',
    '109.248.14.150',
    '45.86.1.53',
    # '188.130.128.149',
    '46.8.212.163',
]



tags_list = get_tag(20000)
count_tags = int(len(tags_list)/len(proxy_ip)+1)
tagsm = np.array_split(tags_list, count_tags)

i = 1
if __name__ == '__main__':
    for im in tagsm:
        # print(im)
        prc = []
        ipr = 0
        for tag in im:
            # if i % 10 == 0 or i == 1:
            proxy = dict()
            proxy['ip'] = proxy_ip[ipr]
            proxy['port'] = '3000'
            proxy['user'] = 'M7MYoO'
            proxy['password'] = '14FXo78cYu'
            proxy['http'] = {'https': f"http://{proxy['user']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"}

            cx = 'f158c7f38d4ef4f06'
            pr = multiprocessing.Process(target=res, args=(i, tag, cx, proxy))
            prc.append(pr)
            pr.start()
            i += 1
            ipr += 1
        for k in prc:
            k.join()
        time.sleep(45)


