import re
import datetime
from telegram import InlineKeyboardButton
import sqlite3


schedule = {
    '0-0': "Пара 1: - \nПара 2: Программирование / Куссуль / БФ-1\nПара 3: Лабораторные программирование / Стасюк / "
           "308-3-1\nПара 4: Матлогика и теория алгоритмов / Ломаченко / 153-16",
    '0-1': "Пара 1: - \nПара 2: Программирование / Куссуль / БФ-1\nПара 3: Лабораторные программирование / Стасюк / "
           "308-3-1\nПара 4: Матлогика и теория алгоритмов / Ломаченко / 153-16",
    '1-0': "Пара 1: -\nПара 2: Математический анализ / Южакова / 107-7\nПара 3: Физика / Кравцов / 114-7\nПара 4: "
           "Вступление в специальность  / Кравцов / 114-7",
    '1-1': "Пара 1: -\nПара 2: Математический анализ / Южакова / 107-7\nПара 3: Физика / Кравцов / 114-7\nПара 4: "
           "Физика / Кравцов / 114-7",
    '2-0': "Пара 1: Алгебра и геометрия / Шумская / 107-7\nПара 2: Абстрактная и прикладная алгебра / Ковальчук / "
           "БФ-1\nПара 3: История науки и техники / Махинько / 142-16\nПара 4:  Физика / Бех / 157-1-16",
    '2-1': "Пара 1: Алгебра и геометрия / Шумская / 107-7\nПара 2: Абстрактная и прикладная алгебра / Ковальчук / "
           "БФ-1\nПара 3: Абстрактная и прикладная алгебра / Ковальчук / 154-1\nПара 4:  Физика / Бех / 157-1-16",
    '3-0': "Пара 1:  Матлогика и теория алгоритмов / Фесенко / 116-7\nПара 2: Алгебра и геометрия / Цвынтарна / "
           "214-11\nПара 3: Математический анализ / Южакова / 107-7\nПара 4: Английский язык / Ящук / 214-11 ",
    '3-1': "Пара 1:  Матлогика и теория алгоритмов / Фесенко / 116-7\nПара 2: Алгебра и геометрия / Цвынтарна / "
           "214-11\nПара 3: -\nПара 4: Английский язык / Ящук / 214-11 ",
    '4-0': "Пара 1: -\nПара 2: Математический анализ / Мирошникова / 153-16\nПара 3: -\nПара 4: -",
    '4-1': "Пара 1: История науки и техники / Махинько / БФ-1\nПара 2: Математический анализ / Мирошникова / "
           "153-16\nПара 3: Лабораторные Физика / Тараненко / 308-4-1\nПара 4: Лабораторные Физика / Тараненко / "
           "308-4-1 ",
    '5-0': "Выходной",
    '5-1': "Выходной",
    '6-0': "Выходной",
    '6-1': "Выходной"
}


def schedule_gen(args=None):
    if args:
        date = datetime.datetime.strptime(args[0], "%d-%m-%Y")
    else:
        date = datetime.datetime.now().date()
    date = str(date.weekday()) + '-' + str(int(date.strftime('%V')) % 2)
    return schedule[date]


def button_gen():
    date = datetime.datetime.now().date()
    date = date - datetime.timedelta(days=date.weekday())
    keyboard = []
    for i in range(3):
        keyboard.append([])
        for k in range(7):
            keyboard[i].append(InlineKeyboardButton(date.strftime("%d"), callback_data=date.strftime('%d-%m-%Y')))
            date += datetime.timedelta(days=1)
    return keyboard


def admins_gen(chatid):
    conn = sqlite3.connect('fibot.db')
    c = conn.cursor()
    mes = ''
    for row in c.execute('SELECT * FROM admins WHERE chatid = ?', [chatid]):
        mes += row[2] + ' ' + row[3] + '\n'
    conn.close()
    return mes


def isAdmin(userid, chatid):
    conn = sqlite3.connect('fibot.db')
    c = conn.cursor()
    for row in c.execute('SELECT * FROM admins WHERE chatid = ?', [chatid]):
        if row[0] == chatid and row[1] == userid:
            return row[2]
    conn.close()
    return None


def admAdd(args):
    conn = sqlite3.connect('fibot.db')
    c = conn.cursor()
    c.execute('INSERT INTO admins (chatid, userid, role, name) VALUES (?, ?, ?, ?)', args)
    conn.commit()
    conn.close()
