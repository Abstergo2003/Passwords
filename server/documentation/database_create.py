import psycopg2

connection = psycopg2.connect(
    database="postgres",
    user="postgres",
    password="docker",
    host="localhost",
    port=5432,
)

cursor = connection.cursor()

f = open("database_create.sql")

sql = f""" {f.read()} """
print(sql)
for stmt in sql.split(";"):
    s = stmt.strip()
    if s:
        cursor.execute(s + ";")

connection.commit()


# f2 = open("mockdata.sql")

# sql2 = f""" {f2.read()} """
# print(sql2)
# for stmt in sql2.split(";"):
#     s = stmt.strip()
#     if s:
#         cursor.execute(s + ";")

connection.commit()
connection.close()
