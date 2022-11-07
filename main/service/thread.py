import multiprocessing
import time
import random
import psycopg2
import numpy as np
from xxxhub import settings

conn = psycopg2.connect(
    dbname=settings.DATABASES['default']['NAME'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    host=settings.DATABASES['default']['HOST']
)

cursor = conn.cursor()


def get_tag():
    cursor.execute("SELECT title FROM main_content WHERE status=0 LIMIT 103")
    return cursor.fetchall()


def test(tag):
    for _ in range(2):
        print(f"{multiprocessing.current_process().name} - {tag}")
        time.sleep(random.randint(2, 5))


prc = []

tags_list = get_tag()
count_tags = round(len(tags_list)/12)
tagsm = np.array_split(tags_list, count_tags)

for im in tagsm:
    ipr = 0
    for ik in im:
        print(ipr, ik)
        ipr += 1
    print(1111)

# if __name__ == '__main__':
#     for tag in get_tag():
#         pr = multiprocessing.Process(target=test, args=(tag,))
#         prc.append(pr)
#         pr.start()
#         count_proc = len(multiprocessing.active_children())
#     for i in prc:
#         i.join()
#     print('Все процессы законченны')