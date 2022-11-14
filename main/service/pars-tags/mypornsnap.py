import requests
import psycopg2
import re
import time
from xxxhub import settings
from bs4 import BeautifulSoup
import multiprocessing.dummy as mp


conn = psycopg2.connect(
    dbname=settings.DATABASES['default']['NAME'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    host=settings.DATABASES['default']['HOST']
)

cursor = conn.cursor()


def set_tag(tag):
    sql = "INSERT INTO main_tags_2 (title, status) VALUES (%s, %s) ON CONFLICT (title) DO NOTHING"
    val = (tag, 0)
    cursor.execute(sql, val)
    conn.commit()


def proxy_len():
    file_proxy = open("../prx_list.txt", "r")
    i = 0
    while True:
        line = file_proxy.readline()
        if not line or '#' in line:
            break
        i += 1
    return i


def proxy_pars(number):
    file_proxy = open("../prx_list.txt", "r")
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


def parse(ass):
    global i
    global src
    number_proc = int(mp.current_process().name.replace('Thread-', ''))
    # number_proc = 3
    proxy = proxy_pars(number_proc-1)
    src = 'porn'
    link_parse = f'https://mypornsnap.xyz/photos/{src}'
    url = link_parse
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; YandexBot/3.0; +http://yandex.com/bots)',
    }
    try:
        r = requests.get(url, headers=headers)
        # links = re.search('You may also like(.+)Search suggestions', r.text, re.MULTILINE | re.DOTALL).group(1)
        soup = BeautifulSoup(r.text, 'lxml')
        tags_div = soup.find('div', 'stags')
        tags = tags_div.find_all('a')
        for tag in tags:
            tt = re.search('">(.+)</a>', str(tag)).group(1).strip()
            set_tag(tt)
            src = tt.replace(" ", "-")
            print(i, tt)
            i += 1
    except:
        pass
    time.sleep(3)



src = 'porn'
i = 1
for _ in range(500):
    pool = mp.Pool(1)
    results = pool.map(parse, 'ass')

    pool.close()
    pool.join()
