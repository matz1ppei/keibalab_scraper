import time
import sqlite3
import requests
from pathlib import Path

BASE_URL = 'https://www.keibalab.jp/db/horse/'
DB_PATH  = './db/keibalab.db'
SAVE_DIR = './html/horse'

def main():

    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        check_horses(c)

        for url, horse_id in get_urls(c):
            time.sleep(1)
            response = fetch(url)
            save(response, horse_id)

    finally:
        conn.close()

def check_horses(c):
    query = 'SELECT count(DISTINCT horse_id) FROM result;'
    result = c.execute(query)
    if not result is None:
        print(result.fetchone()[0])
    else:
        print('No horses')

def get_urls(c):
    query = 'SELECT DISTINCT horse_id FROM result;'
    for id in c.execute(query):
        yield BASE_URL + id[0], id[0]

def fetch(url):
    return requests.get(url)

def save(response, horse_id):

    if not Path(SAVE_DIR).exists():
        Path(SAVE_DIR).mkdir()

    print(response.url, flush=True)

    if response.status_code != 404:
        file_path = SAVE_DIR + '/' + horse_id
        html = open(file_path, 'w', encoding='utf-8')
        html.write(response.text)
        html.close()

if __name__ == '__main__':
    main()
