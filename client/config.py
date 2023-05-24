from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon

class ServerInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Server Settings")
        
        # Creating interface elements
        self.label_address = QLabel("Server Address:")
        self.line_edit_address = QLineEdit()
        self.label_port = QLabel("Server Port:")
        self.line_edit_port = QLineEdit()
        self.button_ok = QPushButton("OK")
        
        self.line_edit_address.setPlaceholderText("localhost")

        # Установка плейсхолдера для порта
        self.line_edit_port.setPlaceholderText("0000")
        # Set window style
        style_file = QtCore.QFile('config.css')
        style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(style_file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)
        self.setFixedSize(260, 160)
        
        # Creating layouts and adding elements
        layout = QVBoxLayout()

        layout.addWidget(self.label_address)
        layout.addWidget(self.line_edit_address)
        layout.addWidget(self.label_port)
        layout.addWidget(self.line_edit_port)
        layout.addWidget(self.button_ok)
        self.setLayout(layout)
        
        self.setWindowIcon(QIcon('chat.png'))
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.button_ok.clicked.connect(self.on_ok_clicked)
        
    def on_ok_clicked(self):
        server_address = self.line_edit_address.text().strip()
        server_port = self.line_edit_port.text().strip()
        if server_address and server_port:
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', 'Empty server address or port. \nPlease enter server details.')
