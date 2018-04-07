import sqlite3


def admins_gen(chatid):
    conn = sqlite3.connect('fibot.db')
    c = conn.cursor()
    mes = ''
    c.execute("CREATE TABLE IF NOT EXISTS admins (chatid INTEGER, userid INTEGER, role TEXT, name TEXT)")
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
