import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from extension import proxies
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from twocaptcha import TwoCaptcha
import requests
import time
import datetime
import re
import json
import psycopg2
# import multiprocessing as mp
import multiprocessing.dummy as mp
from bs4 import BeautifulSoup
from xxxhub import settings


conn = psycopg2.connect(
    dbname=settings.DATABASES['default']['NAME'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    host=settings.DATABASES['default']['HOST']
)

cursor = conn.cursor()


def recaptcha(query, cx, proxy):
    chrome_options = webdriver.ChromeOptions()
    proxies_extension = proxies(proxy['user'], proxy['password'], proxy['ip'], proxy['port'])
    # chrome_options.add_extension(proxies_extension)
    chrome_options.add_argument(f"--proxy-server={proxy['ip']}:{proxy['port']}")
    chrome_options.add_argument("--headless=chrome")

    # navigator = webdriver.Chrome('E:/chromedriver.exe')
    # navigator = webdriver.Chrome('E:/chromedriver.exe', options=chrome_options)
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

    # try:
    navigator.execute_script(f"document.getElementById('g-recaptcha-response').innerHTML = '{res_captcha}'")
    time.sleep(1)
    navigator.execute_script(f"___grecaptcha_cfg.clients[0].Z.Z.callback('{res_captcha}');")
    time.sleep(10)
    # except Exception as e:
    #     pass


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


def cse_tok(cx, proxy):
    data = dict()
    r = requests.get(f'https://cse.google.com/cse.js?hpg=1&cx={cx}', proxies=proxy['http'])
    soup = BeautifulSoup(r.text, 'lxml')
    # cse_token = re.search('cse_token": "(.*)"', r.text, re.MULTILINE)
    try:
        data['cse_token'] = re.search('cse_token": "(.*)"', r.text).group(1)
        data['cselibv'] = re.search('cselibVersion": "(.*)"', r.text).group(1)
    except:
        data['cse_token'] = 0
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
    if cse_token['cse_token'] != 0:
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
            # print(r.text)
            recaptcha(query, cx, proxy)
            # recaptcha()
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
    else:
        return 'Error token'


def res(tag):
    global i
    cx = 'f158c7f38d4ef4f06'
    number_proc = int(mp.current_process().name.replace('Thread-', ''))
    proxy_line = re.search('^(.+?):(.+?)@(.+?):(.+?)$', prx_list[number_proc-1])
    proxy = dict()
    proxy['user'] = proxy_line.group(1)
    proxy['password'] = proxy_line.group(2)
    proxy['ip'] = proxy_line.group(3)
    proxy['port'] = proxy_line.group(4)
    proxy['http'] = {'https': f"http://{proxy['user']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"}
    result = cse_pars(tag, cx, proxy)
    print(i, number_proc, proxy['ip'], tag[1], result)
    i += 1
    time.sleep(45)


def proxy_list():
    file_proxy = open("prx_list.txt", "r")
    proxy = []
    while True:
        line = file_proxy.readline()
        if not line or '#' in line:
            break
        proxy.append(line.replace('\n', ''))
    file_proxy.close
    return proxy


for _ in range(500):
    prx_list = proxy_list()
    count_prx_list = len(prx_list)

    tags_list = get_tag(count_prx_list)

    pool = mp.Pool(count_prx_list)
    i = 1
    results = pool.map(res, tags_list)

    pool.close()
    pool.join()

# pool = mp.Pool(4)
# i = 1
# results = pool.map(res, range(500))
#
# pool.close()
# pool.join()
