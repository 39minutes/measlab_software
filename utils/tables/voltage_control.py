from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from typing import Callable


class VoltageControl(QWidget):
    def __init__(self, on_submit: Callable[[float], None], parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)

        layout.addWidget(QLabel())
        self.input = QLineEdit()
        self.input.setPlaceholderText("U, В")
        re = QRegularExpression(r'^(?:[0-9]|1[0-2])(?:\.[0-9])?$')
        validator = QRegularExpressionValidator(re, self)
        self.input.setValidator(validator)

        btn = QPushButton("Задать")
        btn.clicked.connect(self._on_click)

        layout.addWidget(QLabel("Задать напряжение стенду:"))
        layout.addWidget(self.input)
        layout.addWidget(btn)

        self._on_submit = on_submit

    def _on_click(self):
        txt = self.input.text().strip()
        if not txt:
            QMessageBox.warning(self, "Ошибка", "Введите напряжение")
            return
        try:
            v = float(txt)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Неверный формат числа")
            return

        try:
            self._on_submit(v)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка при отправке", str(e))
        else:
            QMessageBox.information(self, "Готово", f"U={v:.1f}В отправлено")
