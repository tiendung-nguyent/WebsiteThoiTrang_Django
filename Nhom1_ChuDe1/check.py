import sqlite3

# Kết nối tới database
conn = sqlite3.connect('db.sqlite3')

# Sử dụng dấu nháy kép cho tên bảng 'auth_user'
query = "SELECT sql FROM sqlite_master WHERE name='auth_user'"

result = conn.execute(query).fetchone()

if result:
    print(result[0])
else:
    print("Bảng 'auth_user' không tồn tại. Hãy chạy lệnh 'python manage.py migrate' trước.")

conn.close()