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

def parse(id):

    number_proc = int(multiprocessing.current_process().name.replace('SpawnPoolWorker-', ''))
    proxy = proxy_pars(number_proc-1)
    src = 'porn'
    link_parse = f'http://www.shufflesex.com/tags/{id}/{src}'
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

if __name__ == '__main__':
    count_proc = proxy_len()
    with multiprocessing.Pool(count_proc) as p:
        p.map(parse, range(id_tag_start, id_tag_end, -1))

    # s = 1
    # count = len(trends)
    # for trn in trends:
    #     tag = trn.text.strip()
    #     if tag != '':
    #         # set_tag(tag)
    #         link = re.search('tags\/(.+)\/', str(trn)).group(1)
    #         if s == count:
    #             src = tag
    #             link_parse = f'http://www.shufflesex.com/tags/{id_tag}/'
    #         print(link_parse, count, i, tag)
    #         i += 1
    #         id_tag -= 1
