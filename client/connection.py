import json
from socket import socket
from PyQt5 import QtCore


class ListenThread(QtCore.QThread):
    listen_var = QtCore.pyqtSignal(dict)

    def __init__(self, connection: socket, parent=None):
        super(ListenThread, self).__init__(parent)
        self.connection = connection

    def run(self):
        while True:
            data = json.loads(self.connection.recv(8192).decode())
            self.listen_var.emit(data)
