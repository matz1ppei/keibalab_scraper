import sys
import sqlite3
from bs4 import BeautifulSoup
from pathlib import Path

COURSE_NAME = {
    '01': '札幌',
    '02': '函館',
    '03': '福島',
    '04': '新潟',
    '05': '東京',
    '06': '中山',
    '07': '中京',
    '08': '京都',
    '09': '阪神',
    '10': '小倉'
}

def main():

    try:
        conn = sqlite3.connect('./db/keibalab.db')
        c = conn.cursor()
        init_db(c)

        for html in get_html('./html'):
            print(html.name, flush=True)
            race_info = scrape(html)
            if len(race_info) > 0:
                save(c, race_info)

        conn.commit()

    finally:
        conn.close()

def init_db(c):
    create_table_course(c)
    create_table_result(c)
    create_table_payoff(c)

def create_table_course(c):
    c.execute('DROP TABLE IF EXISTS course')
    c.execute("""
        CREATE TABLE course (
            id integer primary key,
            race_id text,
            date text,
            racecourse text,
            number text,
            name text,
            grade text,
            type text,
            distance text,
            weather text,
            going text,
            number_of_horses text
        )
    """)

def create_table_result(c):
    c.execute('DROP TABLE IF EXISTS result')
    c.execute("""
        CREATE TABLE result (
            id integer primary key,
            race_id text,
            ranking text,
            bracket_no text,
            horse_no text,
            horse_id text,
            horse_name text,
            sex text,
            age text,
            weight text,
            jockey_id text,
            jockey text,
            favorite text,
            win_odds text,
            finish text,
            margin text,
            position text,
            final_600 text,
            trainer_id text,
            trainer text,
            horse_weight text
        )
    """)

def create_table_payoff(c):
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

        result_table = soup.find('table', class_='resulttable')
        if not result_table is None:
            course_table = soup.find('div', class_='racedatabox')
            race_info['course'] = scrape_course(course_table, html.name)

            race_info['result'] = scrape_result(result_table, html.name)

            payoff_table = soup.find('div', class_='haraimodoshi').table
            race_info['payoff'] = scrape_payoff(payoff_table, html.name)

    return race_info

def scrape_course(table, file_name):
    course = {'race_id': 'R'+file_name}
    type_distance_number = table.find('ul', class_='classCourseSyokin').find_all('li')[1].text
    name_grade = table.h1.text.strip().replace('\t', '').split('(')
    course['date'] = get_date(table.p.text)
    course['racecourse'] = COURSE_NAME[file_name[8:10]]
    course['number'] = file_name[10:12]
    # ToDo add conditions?
    course['name'] = name_grade[0]
    if len(name_grade) == 1:
        course['grade'] = ''
    else:
        course['grade'] = name_grade[1].split(')')[0]
    course['type'] = type_distance_number[0:1]
    course['distance'] = type_distance_number[1:5]
    course['weather'] = table.ul.find_all('li')[0].text
    course['going'] = table.ul.find_all('li')[1].text
    course['number_of_horses'] = type_distance_number[7:9].split('頭')[0]
    return course

def get_date(text):
    date_text = text.split('\n')[0]
    return date_text.split('(')[0]

def scrape_result(table, file_name):
    result = []
    for i, row in enumerate(table.find_all('tr')):
        # print(row)
        if i > 0:
            columns = row.find_all('td')
            result.append({
                'race_id': 'R'+file_name,
                'ranking': columns[0].text,
                'bracket_no': columns[1].text,
                'horse_no': columns[2].text,
                'horse_id': columns[3].a.get('href').split('/')[3],
                'horse_name': columns[3].text,
                'sex': columns[4].text[0:1],
                'age': columns[4].text[1:2],
                'weight': columns[5].text,
                'jockey_id': columns[6].a.get('href').split('/')[3],
                'jockey': columns[6].text,
                'favorite': columns[7].text,
                'win_odds': columns[8].text.strip(),
                'finish': columns[9].text,
                'margin': columns[10].text.strip(),
                'position': columns[11].text.strip(),
                'final_600': columns[12].text,
                'trainer_id': columns[13].a.get('href').split('/')[3],
                'trainer': columns[13].text,
                'horse_weight': columns[14].text
            })
    return result

def scrape_payoff(table, file_name):
    payoff = {'race_id': 'R'+file_name}
    for i, row in enumerate(table.find_all('tr')):
        columns = row.find_all('td')
        if i == 0:
            payoff['win_r'] = columns[1].text
            payoff['win_p'] = columns[2].text
            payoff['exacta_r'] = columns[4].text
            payoff['exacta_p'] = columns[5].text
        elif i == 1:
            payoff['show_r'] = columns[1].text
            payoff['show_p'] = columns[2].text
            payoff['qplace_r'] = columns[4].text
            payoff['qplace_p'] = columns[5].text
        elif i == 2:
            payoff['bracketq_r'] = columns[1].text
            payoff['bracketq_p'] = columns[2].text
            payoff['trio_r'] = columns[4].text
            payoff['trio_p'] = columns[5].text
        elif i == 3:
            payoff['quinella_r'] = columns[1].text
            payoff['quinella_p'] = columns[2].text
            payoff['trifecta_r'] = columns[4].text
            payoff['trifecta_p'] = columns[5].text

    return payoff

def save(c, race_info):
    insert_course(c, race_info['course'])
    insert_result(c, race_info['result'])
    insert_payoff(c, race_info['payoff'])

def insert_course(c, course):
    c.execute("""
        INSERT INTO course (
            race_id,
            date,
            racecourse,
            number,
            name,
            grade,
            type,
            distance,
            weather,
            going,
            number_of_horses
        )
        VALUES (
            :race_id,
            :date,
            :racecourse,
            :number,
            :name,
            :grade,
            :type,
            :distance,
            :weather,
            :going,
            :number_of_horses
        )
    """, course)

def insert_result(c, result):
    for r in result:
        c.execute("""
           INSERT INTO result (
            race_id,
            ranking,
            bracket_no,
            horse_no,
            horse_id,
            horse_name,
            sex,
            age,
            weight,
            jockey_id,
            jockey,
            favorite,
            win_odds,
            finish,
            margin,
            position,
            final_600,
            trainer_id,
            trainer,
            horse_weight
           )
           VALUES (
            :race_id,
            :ranking,
            :bracket_no,
            :horse_no,
            :horse_id,
            :horse_name,
            :sex,
            :age,
            :weight,
            :jockey_id,
            :jockey,
            :favorite,
            :win_odds,
            :finish,
            :margin,
            :position,
            :final_600,
            :trainer_id,
            :trainer,
            :horse_weight
           ) 
        """,r)

def insert_payoff(c, payoff):
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
