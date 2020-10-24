import os
import sqlite3


def create(f, model):
    conn = sqlite3.connect(f)
    c = conn.cursor()
    c.execute(model)
    conn.commit()
    return conn
