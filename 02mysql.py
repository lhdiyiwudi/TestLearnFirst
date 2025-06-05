import mysql.connector

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="316105",
    database="studentinformation")

mycursor = mydb.cursor()     # create a cursor object

# execute SQL query
# mycursor.execute("SELECT * FROM studentinformation")
# for row in mycursor:
#     print(row)
# mycursor.execute("CREATE TABLE sites (name VARCHAR(255), url VARCHAR(255))")
# mycursor.execute("INSERT INTO sites (name, url) VALUES (%s, %s)", ("Google", "https://www.google.com"))
# mycursor.execute("SHOW TABLES")
# for row in mycursor:
#     print(row)
# mycursor.execute("ALTER TABLE sites ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY")

sql = "INSERT INTO sites (name, url) VALUES (%s, %s)"
val = [
  ('Google', 'https://www.google.com'),
  ('Github', 'https://www.github.com'),
  ('Taobao', 'https://www.taobao.com'),
  ('stackoverflow', 'https://www.stackoverflow.com/')
]
mycursor.executemany(sql, val)

mydb.commit()  # 数据表内容有更新，必须使用到该语句

print(mycursor.rowcount, "记录插入成功。")
print(mycursor.fetchone())
print(mycursor.lastrowid)
print(mycursor.description)
print(mycursor.setoutputsize(1))
mycursor.close()
mydb.close()

