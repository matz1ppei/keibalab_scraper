import argparse
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

START_URL = 'https://www.keibalab.jp/db/race/'
USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36'

def main():
    parser = argparse.ArgumentParser(description='Keibalabの情報を取得する')
    parser.add_argument('from_date', help='YYYYMMDD形式の取得開始日')
    parser.add_argument('to_date', help='YYYYMMDD形式の取得終了日')
    args = parser.parse_args()

    from_date = datetime.strptime(args.from_date, '%Y%m%d')
    to_date = datetime.strptime(args.to_date, '%Y%m%d')

    for race in check_race(from_date, to_date):
        for url, race_id in generate_urls(race):
            time.sleep(1)
            response = fetch(url)
            save(response, race_id)

def check_race(from_date, to_date):
    while(from_date <= to_date):
        response = fetch(START_URL + from_date.strftime('%Y%m%d'))
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup.table is None:
            print(response.url + '/', flush=True)
            for table in soup.find_all('table'):
                cid = COURSE_ID[table.th.text[2:4]]
                yield from_date.strftime('%Y%m%d') + cid
        else:
            time.sleep(1)
        from_date += timedelta(days=1)

def generate_urls(race):
    for racenumber in range(1, 13):
        race_id = race + f'{racenumber:02}'
        url = START_URL + race_id + '/'
        yield url, race_id

def fetch(url):
    headers = {'User-Agent': USER_AGENT}
    return requests.get(url, headers=headers)

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
