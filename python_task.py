import httpx
from dadata import Dadata
import sqlite3


def check_token(token):
    while True:
        try:
            dadata = Dadata(token)
            dadata.suggest("address", "check")
            break
        except (httpx.HTTPStatusError, UnicodeError):
            token = input('Неправильный ключ, повторите ввод\n')
    return token, dadata


def change_settings(dadata, res):
    menu = -1
    while menu != 0:
        print('1 - изменить настройки')
        print('0 - перейти к вводу адреса')
        menu = input()
        if menu not in ['1', '0']:
            print('Некорректный ввод\n')
            continue
        if menu == '0':
            break
        while menu != '0':
            print(f'\n1 - изменить URL, текущий: {res[0]}')
            print(f'2 - изменить ключ')
            print(f'3 - изменить язык, текущий: {res[2]}')
            print('0 - к предыдущему меню\n')
            menu = input()
            if menu not in ['3', '2', '1', '0']:
                print('Некорректный ввод\n')
                continue
            if menu == '0':
                break
            if menu == '1':
                url = input('Введите новый URL\n')
                cur.execute("UPDATE user_settings SET url = ? WHERE url = ?", (url, res[0]))
                res = cur.execute("SELECT * FROM user_settings").fetchone()
            elif menu == '2':
                token = input('Введите новый ключ\n')
                token, dadata = check_token(token)
                cur.execute("UPDATE user_settings SET key = ? WHERE key = ?", (token, res[1]))
                res = cur.execute("SELECT * FROM user_settings").fetchone()
            elif menu == '3':
                lang = input('Введите новый язык\n')
                while lang not in ['en', 'ru']:
                    lang = input('Некорректный ввод, введите en или ru\n')
                cur.execute("UPDATE user_settings SET lang = ? WHERE lang = ?", (lang, res[2]))
                res = cur.execute("SELECT * FROM user_settings").fetchone()
            con.commit()
        menu = '-1'
    lang = cur.execute("SELECT lang FROM user_settings").fetchone()[0]
    return dadata, lang


con = sqlite3.connect("settings.db")
cur = con.cursor()
res = cur.execute("SELECT * FROM user_settings").fetchone()

token = res[1]

if token is None:
    token = input('Введите действующий ключ\n')

token, dadata = check_token(token)

cur.execute("UPDATE user_settings SET key = ? WHERE url = ?", (token, res[0]))

dadata, lang = change_settings(dadata, res)

menu = -1
while menu != '0':
    print('\n1 - ввод адреса')
    print('2 - к предыдущему меню')
    print('0 - выход')
    menu = input()
    if menu not in ['2', '1', '0']:
        print('Некорректный ввод\n')
        continue
    if menu == '0':
        break
    if menu == '2':
        res = cur.execute("SELECT * FROM user_settings").fetchone()
        dadata, lang = change_settings(dadata, res)
        continue
    address = input('Введите адрес\n')
    result = dadata.suggest("address", address, language=lang)
    if not result:
        print('Подходящих адресов не найдено\n')
        continue
    found_addresses = dict()

    for i, r in enumerate(result):
        found_addresses[str(i + 1)] = r['value']
        print(f'{i + 1}) {found_addresses[str(i + 1)]}')

    needed_address = input('\nВыберите подходящий адрес?\n')

    while needed_address not in found_addresses:
        needed_address = input('Такого пункта нет в списке, повторите ввод\n')

    result = dadata.suggest("address", found_addresses[needed_address], count=1)[0]

    geo_lat = result['data']['geo_lat']
    geo_lon = result['data']['geo_lon']
    print('Широта:', geo_lat if geo_lat else 'Нет данных')
    print('Долгота:', geo_lon if geo_lon else 'Нет данных')
