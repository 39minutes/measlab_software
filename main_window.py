# main_window.py
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QWidget, QVBoxLayout, QSizePolicy
)
from PyQt6.QtGui import QFont

from lab5.lab5_window import Lab5Window
from lab18.lab18_window import Lab18Window
from lab16_17.lab1617_window import Lab1617Window


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное меню — Лабораторный стенд")
        self.setMinimumSize(420, 300)
        self.resize(480, 360)

        self.lab5_window    = None
        self.lab1617_window = None
        self.lab18_window   = None

        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        btn_font = QFont("Calibri", 11)

        buttons = [
            (
                "Лабораторная работа\n"
                "«Исследование операционных усилителей,\n"
                "неинвертирующих и инвертирующих усилителей»",
                self.open_lab5,
            ),
            (
                "Лабораторные работы\n"
                "«Дифференциальный усилитель на ОУ»",
                self.open_lab1617,
            ),
            (
                "Лабораторная работа\n"
                "«Исследование инвертирующего и\n"
                "неинвертирующего сумматоров»",
                self.open_lab18,
            ),
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setFont(btn_font)
            btn.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding
            )
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def open_lab5(self):
        if self.lab5_window is None:
            self.lab5_window = Lab5Window()
        self.lab5_window.show()
        self.lab5_window.raise_()
        self.lab5_window.activateWindow()
        self.hide()

    def open_lab1617(self):
        if self.lab1617_window is None:
            self.lab1617_window = Lab1617Window()
        self.lab1617_window.show()
        self.lab1617_window.raise_()
        self.lab1617_window.activateWindow()

    def open_lab18(self):
        if self.lab18_window is None:
            self.lab18_window = Lab18Window()
        self.lab18_window.show()
        self.lab18_window.raise_()
        self.lab18_window.activateWindow()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())