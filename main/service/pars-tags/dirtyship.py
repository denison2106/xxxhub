import requests
import psycopg2
import re
import time
from xxxhub import settings
from bs4 import BeautifulSoup
import multiprocessing


conn = psycopg2.connect(
    dbname=settings.DATABASES['default']['NAME'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    host=settings.DATABASES['default']['HOST']
)

cursor = conn.cursor()


def set_tag(tag):
    sql = "INSERT INTO main_tags (title, status) VALUES (%s, %s) ON CONFLICT (title) DO NOTHING"
    val = (tag, 0)
    cursor.execute(sql, val)
    conn.commit()


src = 'porn'
id_tag_start = 4_900_000
id_tag_end = 4_700_000

def proxy_len():
    file_proxy = open("../proxy.txt", "r")
    i = 0
    while True:
        line = file_proxy.readline()
        if not line or '#' in line:
            break
        i += 1
    return i


def proxy_pars(number):
    file_proxy = open("../proxy.txt", "r")
    proxy = dict()
    i = 0
    while True:
        line = file_proxy.readline()
        if not line or '#' in line:
            break
        if number == i:
            proxy_line = re.search('^(.+?):(.+?)@(.+?):(.+?)$', line)
            proxy['user'] = proxy_line.group(1)
            proxy['password'] = proxy_line.group(2)
            proxy['ip'] = proxy_line.group(3)
            proxy['port'] = proxy_line.group(4)
            proxy['http'] = {'https': f"http://{proxy['user']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"}
        i += 1
    file_proxy.close
    return proxy

def parse():

    number_proc = int(multiprocessing.current_process().name.replace('SpawnPoolWorker-', ''))
    proxy = proxy_pars(number_proc-1)
    src = 'porn'
    link_parse = f'https://dirtyship.com/page/{id}/'
    url = link_parse
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
    }
    r = requests.get(url, proxies=proxy['http'], headers=headers)
    # links = re.search('You may also like(.+)Search suggestions', r.text, re.MULTILINE | re.DOTALL).group(1)
    soup = BeautifulSoup(r.text, 'lxml')
    tag = soup.title.text
    # id_tag -= 1
    if tag.strip() != 'Porn':
        set_tag(tag)
        time.sleep(2)
        print(number_proc, id, tag.strip())
    # trend = links.find_all('a')


i = 1
while i <= 260:
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
    }
    url = f'https://porntn.com/latest-updates/{i}/'
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    tegs = soup.find_all('div', class_='item')
    for tag in tegs:
        tt = re.search('title="(.+?)"', str(tag)).group(1).strip()
        print(i, tt)
        set_tag(tt)
    i += 1
    time.sleep(2)