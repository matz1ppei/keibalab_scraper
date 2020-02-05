import sys
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

def main():
    args = sys.argv

    start_url = 'https://www.keibalab.jp/db/race/'
    from_date = args[1]

    if len(args) < 3:
        to_date = from_date
    else:
        to_date = args[2]

    for url, race_id in generate_urls(start_url, from_date, to_date):
        time.sleep(1)
        response = fetch(url)
        save(response, race_id)

def generate_urls(start_url, from_date_string, to_date_string):
    from_date = datetime.strptime(from_date_string, '%Y%m%d')
    to_date   = datetime.strptime(to_date_string, '%Y%m%d')

    # 8 racecourses, 12 races
    while(from_date <= to_date):
        for racecourse in range(1, 11):
            for racenumber in range(1, 13):
                race_id = from_date.strftime('%Y%m%d') + f'{racecourse:02}' + f'{racenumber:02}'
                url = start_url + race_id + '/'
                yield url, race_id
        from_date += timedelta(days=1)

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
