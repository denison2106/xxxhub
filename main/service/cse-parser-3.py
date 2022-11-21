import multiprocessing
import random
import pytz
import requests
import time
import datetime
import re
import json
import psycopg2
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from twocaptcha import TwoCaptcha
from bs4 import BeautifulSoup

from xxxhub import settings

conn = psycopg2.connect(
    dbname=settings.DATABASES['default']['NAME'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    host=settings.DATABASES['default']['HOST']
)

cursor = conn.cursor()


def proxy_list():
    file_proxy = "proxy.txt"
    proxy = []
    with open(file_proxy) as file:
        for line in file:
            if '#' not in line:
                if not banned_proxy(line):
                    proxy.append(line.replace('\n', ''))
    return proxy


def banned_proxy(proxy):
    proxy_line = re.search('^(.+?):(.+?)@(.+?):(.+?)$', proxy)
    ip_proxy = proxy_line[3]
    if get_banned_proxy(ip_proxy):
        return True
    else:
        return False


def get_banned_proxy(proxy):
    cursor.execute(f"SELECT * FROM main_proxy_banned WHERE ip='{proxy}'")
    res = cursor.fetchall()
    if res:
        date_start = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
        date_end = res[0][2] + datetime.timedelta(hours=3)
        # print(date_start, date_end)
        if date_start > date_end:
            remove_banned_proxy(proxy)
            return False
        else:
            return True
    else:
        return False


def remove_banned_proxy(proxy):
    cursor.execute(f"DELETE FROM main_proxy_banned WHERE ip='{proxy}'")
    conn.commit()


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
    chrome_options.add_argument(f"--proxy-server={proxy['ip']}:{proxy['port']}")
    # chrome_options.add_argument("--headless=chrome")

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
            navigator.execute_script(f"___grecaptcha_cfg.clients[0].K.K.callback('{res_captcha}');")
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
            if row.get('tbLargeUrl'):
                thumb = row['tbLargeUrl'].replace("'", "%27")
            elif row.get('tbMedUrl'):
                thumb = row['tbMedUrl'].replace("'", "%27")
            elif row.get('tbUrl'):
                thumb = row['tbUrl'].replace("'", "%27")
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


def cse_pars(tag, cx, proxy, token_cse):
    # cse_token = cse_tok(cx, proxy)
    cse_token = token_cse
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
        recaptcha(query, cx, proxy)
        print(r.text)
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


def res(i, tag, cs, proxy, token_cse):
    result = cse_pars(tag, cx, proxy, token_cse)
    print(i, proxy['ip'], tag[1], result)


cx = 'f158c7f38d4ef4f06'

i = 1
for _ in range(8):
    prc = []
    ipr = 0

    proxies = proxy_list()
    count_proxies = len(proxies)
    proxy_cse = dict()
    proxy_cse['http'] = {'https': f"http://{proxies[0]}"}
    tags = get_tag(count_proxies)
    token_cse = cse_tok(cx, proxy_cse)

    # proxy_line = re.search('^(.+?):(.+?)@(.+?):(.+?)$', proxies[6])
    # proxy = dict()
    # proxy['user'] = proxy_line.group(1)
    # proxy['password'] = proxy_line.group(2)
    # proxy['ip'] = proxy_line.group(3)
    # proxy['port'] = proxy_line.group(4)
    # proxy['http'] = {'https': f"http://{proxy['user']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"}
    # res(i, tags[0], cx, proxy)

    if __name__ == '__main__':
        for tag in tags:
            proxy_line = re.search('^(.+?):(.+?)@(.+?):(.+?)$', proxies[ipr])
            proxy = dict()
            proxy['user'] = proxy_line.group(1)
            proxy['password'] = proxy_line.group(2)
            proxy['ip'] = proxy_line.group(3)
            proxy['port'] = proxy_line.group(4)
            proxy['http'] = {'https': f"http://{proxy['user']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"}
            pr = multiprocessing.Process(target=res, args=(i, tag, cx, proxy, token_cse))
            prc.append(pr)
            pr.start()
            i += 1
            ipr += 1
        for k in prc:
            k.join()
        time.sleep(45)


