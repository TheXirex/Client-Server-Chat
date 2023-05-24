from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5.QtGui import QIcon

class CustomInputDialog(QDialog):
    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Nickname")
        
        # Creating interface elements
        self.label = QLabel("Enter your nickname:")
        self.line_edit = QLineEdit()
        self.button_ok = QPushButton("OK")

        # Set window style
        style_file = QtCore.QFile('input-nickname.css')
        style_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text)
        stream = QtCore.QTextStream(style_file)
        stylesheet = stream.readAll()
        self.setStyleSheet(stylesheet)
        self.setFixedSize(180, 120)
        
        # Creating layouts and adding elements
        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button_ok)
        self.setLayout(layout)
        
        self.setWindowIcon(QIcon('chat.png'))
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.button_ok.clicked.connect(self.on_ok_clicked)
        
    def on_ok_clicked(self):
        nickname = self.line_edit.text().strip()
        if nickname:
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', 'Empty name. \nPlease enter a nickname.')