import sys
import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from pathlib import Path

COURSE_ID = {
    '札幌': '01',
    '函館': '02',
    '福島': '03',
    '新潟': '04',
    '東京': '05',
    '中山': '06',
    '中京': '07',
    '京都': '08',
    '阪神': '09',
    '小倉': '10'
}

def main():
    args = sys.argv

    start_url = 'https://www.keibalab.jp/db/race/'
    from_date = args[1]

    if len(args) < 3:
        to_date = from_date
    else:
        to_date = args[2]

    for race in check_race(start_url, from_date, to_date):
        for url, race_id in generate_urls(start_url, race):
            time.sleep(1)
            response = fetch(url)
            save(response, race_id)

def check_race(start_url, from_date_str, to_date_str):
    from_date = datetime.strptime(from_date_str, '%Y%m%d')
    to_date   = datetime.strptime(to_date_str, '%Y%m%d')

    while(from_date <= to_date):
        response = fetch(start_url + from_date.strftime('%Y%m%d'))
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup.table is None:
            print(response.url + '/', flush=True)
            for table in soup.find_all('table'):
                cid = COURSE_ID[table.th.text[2:4]]
                yield from_date.strftime('%Y%m%d') + cid
        else:
            time.sleep(1)
        from_date += timedelta(days=1)

def generate_urls(start_url, race):
    for racenumber in range(1, 13):
        race_id = race + f'{racenumber:02}'
        url = start_url + race_id + '/'
        yield url, race_id

def fetch(url):
    return requests.get(url)

def save(response, race_id):

    if not Path('./html').exists():
        Path('./html').mkdir()

    print(response.url, flush=True)

    if response.status_code != 404:
        file_path = './html/' + race_id
        html = open(file_path, 'w', encoding='utf-8')
        html.write(response.text)
        html.close()

if __name__ == '__main__':
    main()
