from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon

class CustomInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nickname")
        
        # Создание элементов интерфейса
        self.label = QLabel("Enter your nickname:")
        self.line_edit = QLineEdit()
        self.button_ok = QPushButton("OK")
        
        # Установка фиксированного размера окна
        self.setFixedSize(200, 120)
        
        self.setStyleSheet('input-nickname.css')
        
        # Создание компоновки и добавление элементов
        layout = QVBoxLayout()

        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.button_ok)

        self.setLayout(layout)
        
        self.setWindowFlags(self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        
        icon = QIcon('chat.png')
        self.setWindowIcon(icon)

        self.button_ok.clicked.connect(self.on_ok_clicked)
        
    def on_ok_clicked(self):
        nickname = self.line_edit.text().strip()
        if nickname:
            self.accept()
        else:
            QMessageBox.critical(self, 'Error', 'Empty name. Please enter a nickname.')
