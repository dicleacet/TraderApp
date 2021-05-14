from sqlite3.dbapi2 import Row
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from login import login_MainWindow
from signUp import Ui_signUp
from admin import Ui_admin
from sellBuy import Ui_sellBuy
import sqlite3

class traderApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(traderApp, self).__init__()
        self.loginForm = login_MainWindow()
        self.loginForm.setupUi(self)
        self.loginForm.log_Button.clicked.connect(self.loginCheck)
        self.loginForm.sign_up_Button.clicked.connect(self.signUpShow)

    def showMessageBox(self,title,message):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setWindowTitle(title)
        msgBox.setText(message)
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec_()

    def insertData(self):
        username = self.signUpForm.username_line.text()
        email = self.signUpForm.mail_line.text()
        password = self.signUpForm.pass_line.text()
        TcNo = self.signUpForm.tc_no_line.text()
        phone = self.signUpForm.phone_line.text()
        name = self.signUpForm.name_line.text()
        adress = self.signUpForm.adress_line.text()
        
        connection = sqlite3.connect('TraderDb.db')
        connection.cursor()
        connection.execute("INSERT INTO USERS VALUES(?,?,?,?,?,?,?,?,?)",(username,email,password,name,TcNo,phone,adress,'0','0'))
        connection.commit()
        connection.close()
        self.showMessageBox('Bilgi','Kayıt işleminiz tamamlandı! Giriş yapabilirsiniz')
        self.signUpWindow.close()

    def signUpShow(self):
        self.signUpWindow = QtWidgets.QDialog()
        self.signUpForm = Ui_signUp()
        self.signUpForm.setupUi(self.signUpWindow)
        self.signUpWindow.show()
        self.signUpForm.signup_Button.clicked.connect(self.insertData)
    
    def adminPanelList(self):
        connection = sqlite3.connect("TraderDb.db")
        pendingProductItem = connection.execute("SELECT * FROM PRODUCTPENDİNG")
        for prod in pendingProductItem:
            self.adminForm.product_listWidget.addItem(prod[0]+" = "+str(prod[1]))
        connection.execute("DELETE FROM PRODUCTPENDİNG")
        self.adminForm.product_listWidget.itemClicked.connect(self.swapProductTable) 
        pendingUserWallet = connection.execute("SELECT * FROM BAKIYEPENDİNG")
        for user in pendingUserWallet:
            self.adminForm.User_Wallet_listWidget.addItem(user[0]+" = "+str(user[1]))
        connection.execute("DELETE FROM BAKIYEPENDİNG")
        self.adminForm.User_Wallet_listWidget.itemClicked.connect(self.swapUserTable)
        connection.commit()
        connection.close()
        
    def swapUserTable(self, item):
        user = item.text().split(" ")
        connection = sqlite3.connect("TraderDb.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM BAKIYEPENDİNG WHERE USERNAME = ? AND BAKİYE = ?",(user[0],user[2])).fetchone()
        cur.execute('UPDATE "USERS" SET HESAPBAKİYE=? WHERE USERNAME=?',(user[2],user[0]))
        connection.commit()
        connection.close()
        self.showMessageBox('Information','Işlem onaylandı!')
        self.adminForm.User_Wallet_listWidget.takeItem(self.adminForm.User_Wallet_listWidget.row(item))

    def swapProductTable(self, item):
        prod = item.text().split(" ")
        connection = sqlite3.connect("TraderDb.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM PRODUCTPENDİNG WHERE USERNAME = ? AND PRODUCTNAME = ?",(prod[0],prod[2])).fetchone()
        cur.execute("INSERT INTO PRODUCT VALUES(?,?,?,?)",(str(i[0]),str(i[1]),str(i[2]),str(i[3])))
        connection.commit()
        connection.close()

    def adminShow(self):
        self.adminWindow = QtWidgets.QDialog()
        self.adminForm = Ui_admin()
        self.adminForm.setupUi(self.adminWindow)
        self.adminWindow.show()
        self.adminPanelList()

    def loginCheck(self):
        self.username = self.loginForm.u_name_line.text()
        self.password = self.loginForm.pass_line.text()
        connection = sqlite3.connect("TraderDb.db")
        result = connection.execute("SELECT * FROM USERS WHERE USERNAME = ? AND PASSWORD = ?",(self.username,self.password))
        adminCheck = connection.execute("SELECT * FROM USERS WHERE ADMIN = ? AND USERNAME = ? ",(1,self.username))
        if(len(result.fetchall())>0):      
            if(len(adminCheck.fetchall())>0):
                self.adminShow()
            else:
                self.sellWindowShow()
            self.close()
        else:
            self.showMessageBox('Warning','Invalid Username And Password')
        connection.close()

    def sellWindowShow(self):
        self.sellWindow = QtWidgets.QMainWindow()
        self.sellBuy = Ui_sellBuy()
        self.sellBuy.setupUi(self.sellWindow)
        connection = sqlite3.connect("TraderDb.db")
        cursor = connection.cursor()
        wallet = cursor.execute("SELECT HESAPBAKİYE FROM USERS WHERE USERNAME = ? AND PASSWORD = ?",(self.username,self.password))
        wallet = wallet.fetchone()
        self.wallet = wallet
        self.sellBuy.viewWallet_label.setText(str(wallet[0]))
        self.sellWindow.show()
        connection.close()
        self.sellBuy.addMoney_pushButton.clicked.connect(self.bakiye)
        self.sellBuy.sell_pushButton.clicked.connect(self.sellit)
        self.sellBuy.buy_control_pushButton.clicked.connect(self.control)
        self.sellBuy.buy_pushButton.clicked.connect(self.buyit)

    def buyit(self):
        ProductName = self.sellBuy.buyproduct_comboBox.currentText()
        UrunBirimi = self.sellBuy.buyquantity_line.text()
        connection = sqlite3.connect("TraderDb.db")
        cursor = connection.cursor()
        if (int(UrunBirimi) < int(self.productCount[0])):
            connection.execute('UPDATE "PRODUCT" SET PRODUCTQUANTİTY=? WHERE USERNAME=? AND PRODUCTNAME = ?',(int(self.productCount[0])-int(UrunBirimi),self.username,ProductName))
            self.showMessageBox('Warning','işleminiz tamamlanmıştır!')
        elif (int(UrunBirimi) == int(self.productCount[0])):
            cursor.execute("DELETE FROM PRODUCT WHERE USERNAME = ? AND PRODUCTNAME = ?",(self.username,ProductName))
            self.showMessageBox('Warning','işleminiz tamamlanmıştır!')
        else:
            self.showMessageBox('Warning', 'Lutfen geçerli bir sayı giriniz!')
        connection.commit()
        connection.close()

    def bakiye(self):
        money = int(self.sellBuy.addMoney_line.text()) + int(self.wallet[0])
        connection = sqlite3.connect("TraderDb.db")
        connection.execute("INSERT INTO BAKIYEPENDİNG VALUES(?,?)",(self.username,money))
        connection.commit()
        connection.close()
        self.showMessageBox('Warning','Bakiye talebiniz alındı! işleminiz onaylandıktan sonra kullanabilirsiniz!')

    def sellit(self):
        Urun = self.sellBuy.sellproduct_comboBox.currentText() 
        UrunBirimi = self.sellBuy.sellquantity_line.text()
        UrunFiyatı = self.sellBuy.sellprice_line.text()
        connection = sqlite3.connect("TraderDb.db")
        connection.execute("INSERT INTO PRODUCTPENDİNG VALUES(?,?,?,?)",(self.username,Urun,UrunFiyatı,UrunBirimi))
        connection.commit()
        self.showMessageBox('Information','Urununuz bekleme listesine alindi')
        connection.close()

    def control(self):
        controlProduct = self.sellBuy.buyproduct_comboBox.currentText()
        connection = sqlite3.connect("TraderDb.db")
        cursor = connection.cursor()
        self.productprice = cursor.execute("SELECT MIN(PRİCE) FROM PRODUCT WHERE PRODUCTNAME = ?",(controlProduct,)).fetchone()
        self.productCount = cursor.execute("SELECT PRODUCTQUANTİTY FROM PRODUCT WHERE PRODUCTNAME = ? AND PRİCE = ?",(controlProduct,self.productprice[0])).fetchone()
        self.showMessageBox('Stok Bilgisi', f"Seçtiğiniz Üründen {self.productCount[0]} tane kalmıştır")
        self.sellBuy.viewPrice_label.setText(str(self.productprice[0]))
        connection.close()

def runApp():
    runApp = QtWidgets.QApplication(sys.argv)
    win = traderApp()
    win.show()
    sys.exit(runApp.exec_())


if __name__ == '__main__':
    runApp()