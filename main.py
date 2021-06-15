import sys, requests
from PyQt5 import QtWidgets
from login import login_MainWindow
from signUp import Ui_signUp
from admin import Ui_admin
from sellBuy import Ui_sellBuy
import sqlite3
from bs4 import BeautifulSoup


class traderApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(traderApp, self).__init__()
        self.loginForm = login_MainWindow()
        self.loginForm.setupUi(self)
        self.loginForm.log_Button.clicked.connect(self.loginCheck)
        self.loginForm.sign_up_Button.clicked.connect(self.signUpShow)

    def showMessageBox(self,title,message):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
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
        self.showMessageBox('Bilgi','Kayıt isleminiz tamamlandı! Giris yapabilirsiniz')
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
            self.adminForm.product_listWidget.addItem(prod[0]+" = "+str(prod[1]+" "+str(prod[2])+" TL'den"+" "+str(prod[3])+" tane"))
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
        self.showMessageBox('Information','Islem onaylandi!')
        self.adminForm.User_Wallet_listWidget.takeItem(self.adminForm.User_Wallet_listWidget.row(item))

    def swapProductTable(self, item):
        prod = item.text().split(" ")
        connection = sqlite3.connect("TraderDb.db")
        cur = connection.cursor()
        cur.execute("SELECT * FROM PRODUCTPENDİNG WHERE USERNAME = ? AND PRODUCTNAME = ?",(prod[0],prod[2])).fetchone()
        cur.execute("INSERT INTO PRODUCT VALUES(?,?,?,?)",(prod[0],prod[2],prod[3],prod[5]))
        connection.commit()
        connection.close()
        self.showMessageBox('Information','Işlem onaylandı!')
        self.adminForm.product_listWidget.takeItem(self.adminForm.product_listWidget.row(item))
    
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
        self.sellWindow.show()
        self.sellBuy.sell_pushButton.clicked.connect(self.sellit)
        self.sellBuy.buy_pushButton.clicked.connect(self.buyit)
        self.sellBuy.exit_button.clicked.connect(self.signOut)
        self.sellBuy.addMoney_button.clicked.connect(self.bakiye)
        self.sellWindow.show()
        self.bakiyeGoster()

    def bakiyeGoster(self):
        connection = sqlite3.connect("TraderDb.db")
        cursor = connection.cursor()
        self.wallet = cursor.execute("SELECT HESAPBAKİYE FROM USERS WHERE USERNAME = ? AND PASSWORD = ?",(self.username,self.password)).fetchone()
        self.sellBuy.money_label_2.setText(str(self.wallet[0]))
        connection.close()

    def signOut(self):
        self.sellWindow.close()
        self.loginForm.u_name_line.setText("")
        self.loginForm.pass_line.setText("")
        self.show()
        
    def buyit(self):
        Urun = self.sellBuy.buyproduct_comboBox.currentText() 
        UrunBirimi = self.sellBuy.buyquantity_line.text()
        UrunFiyatı = self.sellBuy.buyprice_line.text()
        connection = sqlite3.connect("TraderDb.db")
        cursor = connection.cursor()
        try:
            UygunUrunler = cursor.execute("SELECT * FROM PRODUCT WHERE PRODUCTNAME = ?",(Urun,)).fetchone()
            if(UygunUrunler[2]<=int(UrunFiyatı)):
                if(UygunUrunler[3]>int(UrunBirimi)):
                    toplamFiyat = UygunUrunler[2] * int(UrunBirimi)
                    cursor.execute('UPDATE "PRODUCT" SET PRODUCTQUANTİTY=? WHERE USERNAME=? AND PRODUCTNAME = ?',((UygunUrunler[3]-int(UrunBirimi)),UygunUrunler[0],UygunUrunler[1]))
                elif(UygunUrunler[3]==int(UrunBirimi)):
                    toplamFiyat = UygunUrunler[2] * int(UrunBirimi)
                    cursor.execute("DELETE FROM PRODUCT WHERE USERNAME = ? AND PRODUCTNAME = ? AND PRODUCTQUANTİTY=?",(UygunUrunler[0],UygunUrunler[1],UygunUrunler[3]))
                else:
                    toplamFiyat = UygunUrunler[2] * UygunUrunler[3]
                    cursor.execute("DELETE FROM PRODUCT WHERE USERNAME = ? AND PRODUCTNAME = ? AND PRODUCTQUANTİTY=?",(UygunUrunler[0],UygunUrunler[1],UygunUrunler[3]))
                cursor.execute('UPDATE "USERS" SET HESAPBAKİYE=? WHERE USERNAME=?',(self.wallet[0]-toplamFiyat,self.username))
                connection.commit()
                connection.close()
                self.bakiyeGoster()
                self.showMessageBox('Success',f'{Urun} adli urunu icin satın alim islemi tamamlanmistir. Yeni bakiye {round(self.wallet[0],2)}tir')
            else:
                self.showMessageBox('Error','Istediginiz urun bulunamadi')
        except TypeError:
            self.showMessageBox('Error','Istediginiz urun bulunamadi')

    def sellit(self):
        Urun = self.sellBuy.sellproduct_comboBox.currentText() 
        UrunBirimi = self.sellBuy.sellquantity_line.text()
        UrunFiyatı = self.sellBuy.sellprice_line.text()
        connection = sqlite3.connect("TraderDb.db")
        connection.execute("INSERT INTO PRODUCTPENDİNG VALUES(?,?,?,?)",(self.username,Urun,UrunFiyatı,UrunBirimi))
        connection.commit()
        self.showMessageBox('Information','Urununuz bekleme listesine alindi')
        connection.close()

        
    def bakiye(self):
        self.doviz()
        connection = sqlite3.connect("TraderDb.db")
        connection.execute("INSERT INTO BAKIYEPENDİNG VALUES(?,?)",(self.username,self.kullaniciCuzdan))
        connection.commit()
        connection.close()
        self.showMessageBox('Information','Bakiye talebiniz alındı! işleminiz onaylandıktan sonra kullanabilirsiniz!')


    def doviz(self):     
        sayfa = requests.get("https://www.doviz.com/")
        Kurlar = BeautifulSoup(sayfa.content,"html.parser")
        Dolar = Kurlar.find("span",{"data-socket-key":"USD"}).text.replace(",",".")
        Euro = Kurlar.find("span",{"data-socket-key":"EUR"}).text.replace(",",".")
        Sterlin = Kurlar.find("span",{"data-socket-key":"GBP"}).text.replace(",",".")
        doviz = self.sellBuy.addmoney_comboBox.currentText()
        miktar = self.sellBuy.addMoney_line.text()
        if (doviz == "DOLAR"):
            self.kullaniciCuzdan = float(Dolar) * int(miktar)
        elif (doviz == "EURO"):
            self.kullaniciCuzdan = float(Euro) * int(miktar)
        elif (doviz == "STERLIN"):
            self.kullaniciCuzdan = float(Sterlin) * int(miktar)
        else:
            self.kullaniciCuzdan = int(miktar)



def runApp():
    runApp = QtWidgets.QApplication(sys.argv)
    win = traderApp()
    win.show()
    sys.exit(runApp.exec_())


if __name__ == '__main__':
    runApp()