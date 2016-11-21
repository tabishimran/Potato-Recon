#!/usr/bin/python3
import string
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from form2 import Ui_MainWindow
from sys import argv
import requests
from bs4 import BeautifulSoup
import re
import subprocess
import os
import urllib

search="http://google.co.in/search?q="

def getfcc(query):
    fcc_list=[]
    page = requests.get(search+query+"+fcc+id")
    response=page.text
    soup=BeautifulSoup(response,"lxml")
    text=soup.get_text()
    list=re.findall("FCC ID[:, ][^a-z,/.()]* ",text)
    for x in list:
        if len(x)>10:
            x=x.replace(":","")
            fcc_list.append(x)
    if len(fcc_list)<=1:
        return "FCC ID NOT FOUND"
    max=0
    id=fcc_list[0]
    for x in fcc_list:
        if(max<fcc_list.count(x)):
            max=fcc_list.count(x)
            id=x
    return id

class Myclass(Ui_MainWindow):
        a={}
        inva={}
        fcc_id=""
        def __init__(self, dialog):
                Ui_MainWindow.__init__(self)
                self.setupUi(dialog)
                self.pushButton.clicked.connect(self.getfccid)
                self.pushButton_2.clicked.connect(self.getexhibits)
                self.pushButton_3.clicked.connect(self.download_exhibits)

        def getfccid(self):
                global fcc_id
                print("getfccid called")
                self.label_2.setText("Looking up FCC ID")
                query=self.lineEdit.text()
                fcc_id=getfcc(query)
                if fcc_id!="FCC ID NOT FOUND":
                    self.lineEdit_2.setText(fcc_id)
                    self.label_2.setText("FCC ID lookup Successful")
                    self.pushButton_2.setEnabled(True)
                else:
                    self.lineEdit_2.setText(fcc_id)
                    self.label_2.setText("FCC ID lookup Failed")

        def getexhibits(self):
            global a
            global inva
            global fcc_id
            print("getexhibits called")
            fcc_id=fcc_id.replace(" ","")
            fcc_id=fcc_id.replace("FCCID","")
            self.label_2.setText("Looking up FCC database for resources")
            out=requests.get("https://fccid.io/"+str(fcc_id))
            print("https://fccid.io/"+fcc_id)
            soup=BeautifulSoup(out.text,"lxml")
            output=soup.find("div",{"id":"Exhibits"})
            table=output.table
            url_list=[]
            for row in table.findAll("td"):
                 if row.a:
                     url_list.append(row)
            text=[]
            for i in url_list:
                 text.append(i.text)
            urls=[]
            for u in url_list:
                urls.append(u.a.get("href"))
            self.listWidget.setEnabled(True)
            self.listWidget.setSelectionMode(2)
            self.pushButton_3.setEnabled(True)
            a=dict(zip(text,urls))
            inva=dict(zip(urls,text))
            for i in a:
                self.listWidget.addItem(">> "+str(i))
            checked_items=[]
            self.label_2.setText("FCC Database lookup Successful")


        def download_exhibits(self):
            global a
            global inva
            print("download_exhibits called")
            s=requests.Session()
            download_urls=[]
            items = self.listWidget.selectedItems()
            x=[]
            for i in list(items):
                x.append(str(i.text()).replace(">> ",""))
                for count in x:
                    download_urls.append(a[count])
            dirname=self.lineEdit.text()
            dirname=str(dirname).replace(" ","-")
            os.makedirs(dirname)
            os.chdir(dirname)
            for x in download_urls:
                self.label_2.setText("Downloading "+str(inva[x]))
                subprocess.Popen(['wget','-q','-O',str(inva[x])+".pdf",x.replace("document","pdf")])

            query=self.lineEdit.text()   
            self.label_2.setText("Downloads will be saved in ~/"+str(query.replace(" ","+")))




if __name__ == "__main__":
        app = QtWidgets.QApplication(sys.argv)
        app.setWindowIcon(QtGui.QIcon("/home/txjoe/fccrecon/logo.png"))
        dialog = QtWidgets.QMainWindow()
        prog = Myclass(dialog)
        dialog.show()
        sys.exit(app.exec_())

