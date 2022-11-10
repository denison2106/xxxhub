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

proxy_ip = [
    # '45.11.20.240',
    '188.130.142.101',
    '109.248.55.203',
    '45.87.252.124',
    '46.8.106.138',
    '46.8.57.191',
    '109.248.142.51',
    '185.181.245.75',
    '46.8.11.101',
    '46.8.23.236',
    '92.119.193.16',
    '45.11.20.3',
    '45.15.73.169',
    '188.130.143.222',
    '109.248.205.8',
    '188.130.142.249',
    '109.248.128.218',
    '46.8.106.70',
    '46.8.223.3',
    '188.130.137.13',
]

src = 'porn'
id_tag_start = 4952002
id_tag_end = 4900000


def parse(id):

    number_proc = int(multiprocessing.current_process().name.replace('SpawnPoolWorker-', ''))
    proxy = dict()
    proxy['ip'] = proxy_ip[number_proc-1]
    proxy['port'] = '5500'
    proxy['user'] = 'gFRKCO'
    proxy['password'] = 'OP13iimKcj'
    proxy['http'] = {'https': f"http://{proxy['user']}:{proxy['password']}@{proxy['ip']}:{proxy['port']}"}

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
    count_proc = len(proxy_ip)
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
