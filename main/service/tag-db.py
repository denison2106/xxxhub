import psycopg2
from xxxhub import settings

conn = psycopg2.connect(
    dbname='candyhub',
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    host=settings.DATABASES['default']['HOST']
)

cursor = conn.cursor()

conn2 = psycopg2.connect(
    dbname=settings.DATABASES['default']['NAME'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    host=settings.DATABASES['default']['HOST']
)

cursor2 = conn2.cursor()


def insert_tag(tag, status=0):
    sql = "INSERT INTO main_content (title, status) VALUES (%s, %s) " \
          "ON CONFLICT (title) DO NOTHING"
    val = (tag, status)
    cursor2.execute(sql, val)
    conn2.commit()


def get_tag():
    cursor.execute("SELECT * FROM main_tagspars WHERE approve=True AND LENGTH(tag)>15 ORDER BY LENGTH(tag) ASC")
    return cursor.fetchall()

i = 1
for row in get_tag():
    insert_tag(row[1])
    print(i, row)
    i += 1
