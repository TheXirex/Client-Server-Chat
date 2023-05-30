import json
import time
import sys
from socket import socket

from PyQt5 import QtCore
from PyQt5.QtWidgets import QMainWindow, QPushButton, QTextEdit, QLabel, QVBoxLayout, \
    QScrollArea, QWidget, QMessageBox, QApplication, QDesktopWidget

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QFile, Qt
from PyQt5.uic import loadUi

from connection import ListenThread
from input_nickname import CustomInputDialog
from config import ServerInputDialog

ADDRESS = ''
PORT = 0
MESSAGES = dict()

class UI(QMainWindow):
    def __init__(self):
        super(UI, self).__init__()

        ui_file = QFile("client.ui")
        ui_file.open(QFile.ReadOnly)
        loadUi(ui_file, self)
        ui_file.close()

        self.send_button = self.findChild(QPushButton, "send_button")
        self.send_button.clicked.connect(self.SendButton)

        self.send_text = self.findChild(QTextEdit, "text_send")
        self.send_text.installEventFilter(self)

        self.print_text = self.findChild(QTextEdit, "text_show")

        self.nickname = self.findChild(QLabel, "nick_label")

        self.Users = self.findChild(QScrollArea, "UsersMessages")
        
        self.sendto = self.findChild(QTextEdit, "send_to")
        self.sendto.installEventFilter(self)

        style_file = QtCore.QFile('client.css')
        style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(style_file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)
        self.setWindowIcon(QIcon('chat.png'))
        
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, False)

        self.setFixedSize(self.width(), self.height())

        self.show()

        window_geometry = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

        self.inputServer()

        self.Connection = socket()
        self.Connection.connect((ADDRESS, PORT))

        self.inputNick()

        self.vbox = QVBoxLayout()
        self.widget = QWidget()

        self.listenThread = ListenThread(self.Connection)
        self.listenThread.listen_var.connect(self.ServerResponse)
        self.listenThread.start()

        self.user_choose = ""

    def ServerResponse(self, data: dict):
        if data["code"] == "receive":
            sender = data['from']
            message = data['message']
            if sender in MESSAGES:
                MESSAGES[sender]['message'].append(["user", message])
                if self.user_choose == sender:
                    self.print_text.append(message)
                else:
                    MESSAGES[sender]['button'].setStyleSheet('background: rgb(255,0,0);')
            else:
                MESSAGES[sender] = {
                    'button': self.addUser(sender),
                    'message': [["user", message]],
                    'read': False
                }
                if self.user_choose != sender:
                    MESSAGES[sender]['button'].setStyleSheet('background: rgb(255,0,0);')
                else:
                    self.print_text.append(message)

        if data["code"] == "error":
            QMessageBox.critical(self, "Error", data['message'], QMessageBox.Ok)
            self.sendto.clear()

        if data["code"] == "user":
            MESSAGES[data['message']] = {
                'button': self.addUser(data['message']),
                'message': [],
                'read': True
            }
            MESSAGES[data['message']]['button'].setStyleSheet('background: rgb(255,255,255);')

    def inputServer(self):
        while True:
            dialog = ServerInputDialog(self)
            ok = dialog.exec_()
            if ok:
                server_address = dialog.line_edit_address.text().strip()
                server_port = dialog.line_edit_port.text().strip()
                if server_address and server_port:
                    if server_port.isdigit():
                        global ADDRESS, PORT
                        ADDRESS = server_address
                        PORT = int(server_port)
                        break
                    else:
                        QMessageBox.critical(self, 'Error', 'Invalid port number. Please enter a valid port.')
                else:
                    QMessageBox.critical(self, 'Error', 'Empty server address or port. Please enter server details.')
            else:
                self.closeEvent(None)
                break

    def inputNick(self):
        while True:
            dialog = CustomInputDialog(self)
            ok = dialog.exec_()
            if ok:
                self.nick = dialog.line_edit.text().strip()
                if self.nick:
                    self.ServerSend("nick", message=self.nick)
                    self.nickname.setText(f"Your nickname: {self.nick}")
                    break
                else:
                    QMessageBox.critical(self, 'Error', 'Empty name. Please enter a nickname.')
            else:
                self.closeEvent()
                break
    
    def SendButton(self):
        message = self.send_text.toPlainText().strip()
        if self.user_choose != "" and message:
            full_message = f"{self.nick}: {message}"
            self.ServerSend("send", self.user_choose, full_message)
            if self.user_choose in MESSAGES:
                user_button = MESSAGES[self.user_choose]['button']
                if user_button is not None:
                    MESSAGES[self.user_choose]['message'].append(["me", full_message])
                    self.print_text.append(full_message)
            self.send_text.clear()

    def ServerSend(self, code: str, to: str = "server", message: str = ""):
        dict_send = {"code": code,
                     "from": self.nick,
                     "to": to,
                     "message": message}

        self.Connection.send(json.dumps(dict_send).encode())

    def closeEvent(self, event):
        self.ServerSend("exit")
        time.sleep(1)
        self.Connection.close()
        super().closeEvent(event)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress and obj is self.send_text:
            if event.key() == QtCore.Qt.Key_Return and self.send_text.hasFocus():
                self.SendButton()
                self.send_text.clear()
        if event.type() == QtCore.QEvent.KeyPress and obj is self.sendto:
            if event.key() == QtCore.Qt.Key_Return and self.sendto.hasFocus():
                self.ServerSend("find", message=self.sendto.toPlainText())
                self.sendto.clear()
        return super().eventFilter(obj, event)

    def UserProcess(self, name: str):
        self.user_choose = name
        self.print_text.clear()
        MESSAGES[name]['button'].setStyleSheet('background: rgb(255,255,255);')
        if len(MESSAGES[name]['message']) != 0:
            for i in MESSAGES[name]['message']:
                self.print_text.append(i[1])


    def addUser(self, name: str):
    
        if name in MESSAGES:
            QMessageBox.information(self, "User Exists", "This user already exists.")
            self.sendto.clear()
            return MESSAGES[name]['button']
    
        button = QPushButton(self)
        button.setText(name.split(":")[0])
        button.clicked.connect(lambda _, name=name: self.UserProcess(name))

        self.vbox.addWidget(button)
        self.widget.setLayout(self.vbox)
        self.Users.setWidget(self.widget)
        self.sendto.clear()

        MESSAGES[name] = {
            'button': button,
            'message': [],
            'read': True
        }
        MESSAGES[name]['button'].setStyleSheet('background: rgb(255,255,255);')

        return button

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec()
    
