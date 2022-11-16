import psycopg2
from xxxhub import settings

conn = psycopg2.connect(
    dbname=settings.DATABASES['default']['NAME'],
    user=settings.DATABASES['default']['USER'],
    password=settings.DATABASES['default']['PASSWORD'],
    host=settings.DATABASES['default']['HOST']
)

cursor = conn.cursor()


def insert_tag(tag, status=0):
    sql = "INSERT INTO main_content (title, status) VALUES (%s, %s) " \
          "ON CONFLICT (title) DO NOTHING"
    val = (tag, status)
    cursor.execute(sql, val)
    conn.commit()


def update_tag(id, status):
    sql = f"UPDATE main_tags SET status = {status} WHERE id = '{id}'"
    cursor.execute(sql)
    conn.commit()


def get_tag():
    # cursor.execute("SELECT * FROM main_tags WHERE status=0 AND LENGTH(title)>15 ORDER BY LENGTH(title) DESC LIMIT 2000")
    # cursor.execute("SELECT * FROM main_tags WHERE status=0 AND LENGTH(title)>15 ORDER BY id ASC LIMIT 10000")
    cursor.execute("SELECT * FROM main_tags WHERE status=0 ORDER BY id DESC LIMIT 5000")
    return cursor.fetchall()

i = 1
file = open("keys.txt", encoding="utf8")
i = 1
for tag in file:
    tag = tag.replace('\n', '').replace('"', '')
    insert_tag(tag)
    print(i, tag)
    i += 1
file.close
    # update_tag(row[0], 1)
    # i += 1
