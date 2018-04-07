"""Copyright 2018 Eugene Litvin

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License."""


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
