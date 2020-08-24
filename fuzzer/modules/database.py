import os
import sqlite3


def init(f):
    if os.path.isfile(f):
        os.remove(f)
    conn = sqlite3.connect(f)
    c = conn.cursor()
    c.execute('''CREATE TABLE results (id INT, my_var1 TEXT, my_var2 TEXT)''')
    conn.commit()
    conn.close()
