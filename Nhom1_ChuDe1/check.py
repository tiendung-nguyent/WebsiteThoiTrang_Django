import sqlite3
conn=sqlite3.connect('db.sqlite3')
print(conn.execute('SELECT sql FROM sqlite_master WHERE name='auth_user'').fetchone()[0])
