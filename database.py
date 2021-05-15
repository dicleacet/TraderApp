import sqlite3 

def createTable():
    connection = sqlite3.connect('TraderDb.db')
    connection.cursor()
    connection.execute("CREATE TABLE USERS (USERNAME TEXT NOT NULL, EMAIL TEXT, PASSWORD TEXT, NAME TEXT, TC İNT, PHONE İNT, ADRESS TEXT, ADMIN İNT, HESAPBAKİYE İNT)")
    connection.execute("CREATE TABLE PRODUCT(USERNAME TEXT,PRODUCTNAME TEXT,PRİCE İNT, PRODUCTQUANTİTY İNT)")
    connection.execute("INSERT INTO USERS VALUES(?,?,?,?,?,?,?,?,?)",('dicle','dicle@gmail.com','123','dicleacet','12112112112','05055050550','izmir','1','30000'))
    connection.commit()
    connection.execute("CREATE TABLE BAKIYEPENDİNG (USERNAME TEXT NOT NULL, BAKİYE İNT)")
    connection.execute("CREATE TABLE PRODUCTPENDİNG(USERNAME TEXT,PRODUCTNAME TEXT,PRİCE İNT, PRODUCTQUANTİTY İNT)")
    result = connection.execute("SELECT * FROM USERS")
    for data in result:
        print("Username: " ,data[0])
        print("Email: ", data[1])
        print("Password: ", data[2])


    connection.close()

createTable()


