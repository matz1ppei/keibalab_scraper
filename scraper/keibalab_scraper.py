import sys
import sqlite3
from bs4 import BeautifulSoup
from pathlib import Path

RESULT_SELECTOR = 'div.RaceTableWrap > table '
PAYOFF_SELECTOR = 'div.haraimodoshi > table '

def main():
    args = sys.argv

    try:
        conn = sqlite3.connect('./db/keibalab.db')
        c = conn.cursor()
        init_db(c)

        for html in get_html('./html'):
            print(html.name, flush=True)
            race_info = scrape(html)
            save(c, race_info)

        conn.commit()

    finally:
        conn.close()

def init_db(c):
    init_course(c)
    init_result(c)
    init_payoff(c)


def init_course(c):
    pass

def init_result(c):
    c.execute('DROP TABLE IF EXISTS result')
    c.execute("""
        CREATE TABLE result (
            id integer primary key,
            race_id text,
            ranking text,
            bracket_no text,
            horse_no text,
            horse_name text,
            sex text,
            age text,
            weight text,
            jockey text,
            favorite text,
            win_odds text,
            finish text,
            margin text,
            position text,
            final_600 text,
            trainer text,
            horse_weight text
        )
    """)

def init_payoff(c):
    c.execute('DROP TABLE IF EXISTS payoff')
    c.execute("""
        CREATE TABLE payoff (
            id integer primary key,
            race_id text,
            win_r text,
            win_p text,
            show_r text,
            show_p text,
            bracketq_r text,
            bracketq_p text,
            quinella_r text,
            quinella_p text,
            exacta_r text,
            exacta_p text,
            trio_r text,
            trio_p text,
            trifecta_r text,
            trifecta_p text
        )
    """)

def get_html(folder_path):
    for html in Path(folder_path).iterdir():
        yield html

def scrape(html):
    with open(html, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        race_info = {}
        race_info['course'] = scrape_course(soup.find('div', class_='racedatabox'))
        race_info['result'] = scrape_result(soup.find('table', class_='resulttable'))

        """
        race_info = {
            'result': {
                'race_id': 'R' + html.name,
                'ranking': soup.select_one(RESULT_SELECTOR + 'tr:nth-child(1) > td:nth-child(1)').get_text(),
                'bracket_no': soup.select_one(RESULT_SELECTOR + 'tr:nth-child(1) > td:nth-child(2)').get_text(),
                'horse_no': soup.select_one(RESULT_SELECTOR + 'tr:nth-child(1) > td:nth-child(3)').get_text()
            },
            'payoff': {
                'race_id': 'R' + html.name,
                'win_r': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(1) > td:nth-child(2)').get_text(),
                'win_p': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(1) > td:nth-child(3)').get_text(),
                'show_r': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(2) > td:nth-child(2)').get_text(),
                'show_p': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(2) > td:nth-child(3)').get_text(),
                'bracketq_r': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(3) > td:nth-child(2)').get_text(),
                'bracketq_p': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(3) > td:nth-child(3)').get_text(),
                'quinella_r': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(4) > td:nth-child(2)').get_text(),
                'quinella_p': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(4) > td:nth-child(3)').get_text(),
                'exacta_r': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(1) > td:nth-child(5)').get_text(),
                'exacta_p': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(1) > td:nth-child(6)').get_text(),
                'trio_r': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(3) > td:nth-child(5)').get_text(),
                'trio_p': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(3) > td:nth-child(6)').get_text(),
                'trifecta_r': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(4) > td:nth-child(5)').get_text(),
                'trifecta_p': soup.select_one(PAYOFF_SELECTOR + 'tr:nth-child(4) > td:nth-child(6)').get_text()
            }
        }
        """

        return race_info

def scrape_course(table):
    pass

def scrape_result(table):
    for row in table.findAll('tr'):
        for column in row.findAll('td'):
            pass

def scrape_payoff(table):
    pass


def save(c, race_info):
    save_course(c, race_info['course'])
    save_result(c, race_info['result'])
    save_payoff(c, race_info['payoff'])

def save_course(c, course):
    c.execute("""

    """, course)

    pass

def save_result(c, result):
    for r in result:
        c.execute("""
           INSERT INTO result (
            race_id,
            ranking,
            bracket_no,
            horse_no,
            horse_name,
            sex,
            age,
            weight,
            jockey,
            favorite,
            win_odds,
            finish,
            margin,
            position,
            final_600,
            trainer,
            horse_weight
           )
           VALUES (
            :race_id,
            :ranking,
            :bracket_no,
            :horse_no,
            :horse_name,
            :sex,
            :age,
            :weight,
            :jockey,
            :favorite,
            :win_odds,
            :finish,
            :margin,
            :position,
            :final_600,
            :trainer,
            :horse_weight
           ) 
        """,r)

def save_payoff(c, payoff):
    c.execute("""
        INSERT INTO payoff (
            race_id,
            win_r,
            win_p,
            show_r,
            show_p,
            bracketq_r,
            bracketq_p,
            quinella_r,
            quinella_p,
            exacta_r,
            exacta_p,
            trio_r,
            trio_p,
            trifecta_r,
            trifecta_p
        )
        VALUES (
            :race_id,
            :win_r,
            :win_p,
            :show_r,
            :show_p,
            :bracketq_r,
            :bracketq_p,
            :quinella_r,
            :quinella_p,
            :exacta_r,
            :exacta_p,
            :trio_r,
            :trio_p,
            :trifecta_r,
            :trifecta_p
        )
    """, payoff)

if __name__ == '__main__':
    main()