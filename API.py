import sys
import json
import requests
import sqlite3


def insert_query():
    c.execute('DELETE FROM sqlitedb_developers')
    conn.commit()

    # Базовый URL к сервису dadata
    BASE_URL = 'https://suggestions.dadata.ru/suggestions/api/4_1/rs/suggest/'
    # API токен с сайта
    API_KEY = input("Введите свой API ключ: ")
    # Язык, на котором возвращается ответ
    while True:
        language = input("Выберите язык ru/en: ")
        if language == 'ru' or language == 'en':
            break
        else:
            print('Введите правильно команду!')
            print('-----------------------------------------------------------------')

    # c.execute('''DROP TABLE sqlitedb_developers''')
    insert_query = """INSERT INTO  sqlitedb_developers        
                (id, URL, API_KEY, language) VALUES (?, ?, ?, ?)"""
    insert = (1, BASE_URL, API_KEY, language)
    c.execute(insert_query, insert)
    print('Данные успешно добавлены \n')
    conn.commit()


try:
    conn = sqlite3.connect('sqlite_python.db')
    c = conn.cursor()
    c.execute('''SELECT count(name) FROM sqlite_master WHERE type='table' AND name='sqlitedb_developers' ''')
    if c.fetchone()[0] == 1:
        insert_query()
    else:
        create_table_query = '''CREATE TABLE sqlitedb_developers (
                                id INTEGER PRIMARY KEY,
                                URL TEXT NOT NULL,
                                API_KEY TEXT NOT NULL,
                                language VARCHAR NOT NULL);'''
        c.execute(create_table_query)
        insert_query()
    conn.commit()
    c.close()
except sqlite3.Error as error:
    print("Ошибка при подключении к SQLite", error)


# Поиск адреса
def find_address(resource, query):
    select_query = """SELECT * from sqlitedb_developers"""
    c = conn.cursor()
    c.execute(select_query)
    conn.commit()
    records = c.fetchall()
    c.close()
    for row in records:
        BASE_URL = row[1]
        API_KEY = row[2]
        language = row[3]
    url = BASE_URL + resource
    headers = {
        'Authorization': 'Token ' + API_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    data = {
        'query': query,
        'language': language
    }
    res = requests.post(url, data=json.dumps(data), headers=headers)
    return res.json()


# Сортировка найденых адресов
def sort_address(data):
    sorted_addresses = {}
    a = 1
    try:
        for row in data['suggestions']:
            addresses = {}
            addresses['value'] = str(row['value'])
            addresses['geo_lat'] = row['data']['geo_lat']
            addresses['geo_lon'] = row['data']['geo_lon']
            sorted_addresses[a] = addresses
            a += 1
    except KeyError:
        print('Неправильно ввели API ключ!')
        API_KEY = input("Введите свой API ключ: ")
        c = conn.cursor()
        update_query = """Update sqlitedb_developers set API_KEY = ? where id = 1"""
        api = (API_KEY,)
        c.execute(update_query, api)
        print('Данные успешно изменены \n')
        conn.commit()
        c.close()
    return sorted_addresses


# Изменение настроек
def settings():
    while True:
        print('-----------------------------------------------------------------')
        print('API ключ - api')
        print('Язык - lang')
        print('Выход - exit')
        print('-----------------------------------------------------------------')
        command = input('Выберите одну из команд: ')
        c = conn.cursor()
        if command == 'api':
            API_KEY = input("Введите свой API ключ: ")
            update_query = """Update sqlitedb_developers set API_KEY = ? where id = 1"""
            api = (API_KEY,)
            c.execute(update_query, api)
            conn.commit()
            print('Данные успешно изменены \n')
        elif command == 'lang':
            while True:
                language = input("Выберите язык ru/en: ")
                if language == 'ru' or language == 'en':
                    update_query = """Update sqlitedb_developers set language = ? where id = 1"""
                    lang = (language,)
                    c.execute(update_query, lang)
                    conn.commit()
                    print('Данные успешно изменены \n')
                    break
                else:
                    print("Введите правильно команду")
        elif command == 'exit':
            c.close()
            break
        else:
            print('Введите правильную команду')


stdin_fileno = sys.stdin

while True:
    print('-----------------------------------------------------------------')
    print('Настройки - settings')
    print('Выход - exit')
    print('-----------------------------------------------------------------')
    print('Введите адрес или команду: ')
    for line in stdin_fileno:
        if line.strip() == 'exit':
            print('Завершение программы')
            conn.close()
            exit(0)
        elif line.strip() == 'settings':
            settings()
        else:
            data = find_address('address', line)
            result = sort_address(data)
            if not result:
                print('Данный адрес не найден!')
            elif len(result) == 1:
                print(str(result[1]['value'] + ': широта - ' + str(result[1]['geo_lat']) + '; долгота - ' + str(
                    result[1]['geo_lon'])))
            else:
                for i in result:
                    print(str(i) + ' - ' + str(result[i]['value']))
                while True:
                    try:
                        number = int(input('Введите цифру вашего адреса: '))
                        if number in result:
                            print(str(result[number]['value'] + ': широта - ' + str(
                                result[number]['geo_lat']) + '; долгота - ' + str(result[number]['geo_lon']) + '\n'))
                            break
                        else:
                            print('Неправильно ввели номер!')
                    except ValueError:
                        print('Введите номер!')
        break



