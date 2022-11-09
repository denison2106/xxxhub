import requests
import psycopg2
from xxxhub import settings
from bs4 import BeautifulSoup


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

for _ in range(1000):
    url = f'https://3gpking.name/tube+{src}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    trends = soup.find('div', class_='trends')
    trend = trends.find_all('li', class_='trend')

    i = 1
    for trn in trend:
        tag = trn.text.strip()
        set_tag(tag)

        if i == 1:
            src = tag

        print(i, tag)
        i += 1
