import sqlite3

connection = sqlite3.connect("TraderDb.db")
cursor = connection.cursor()       
product = cursor.execute("INSERT INTO PRODUCT VALUES(?,?,?,?)",("rafik","Arpa",1,33))
connection.commit()
connection.close()