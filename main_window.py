import sys
import serial.tools.list_ports

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton,
    QWidget, QVBoxLayout, QSizePolicy,
    QDialog, QVBoxLayout, QLabel, QComboBox,
    QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QSettings, Qt
from lab5.lab5_window import Lab5Window
from lab18.lab18_window import Lab18Window
from lab16_17.lab1617_window import Lab1617Window
from utils.stand_controller import StandController


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное меню — Лабораторный стенд")
        self.setMinimumSize(420, 300)
        self.resize(480, 360)

        self.lab5_window = None
        self.lab1617_window = None
        self.lab18_window = None

        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        btn_font = QFont("Calibri", 11)

        # === Только 3 большие кнопки лабораторных работ ===
        buttons = [
            ("Лабораторная работа\n«Исследование операционных усилителей,\nнеинвертирующих и инвертирующих усилителей»",
             self.open_lab5),
            ("Лабораторные работы\n«Дифференциальный усилитель на ОУ»", self.open_lab1617),
            ("Лабораторная работа\n«Исследование инвертирующего и\nнеинвертирующего сумматоров»", self.open_lab18),
        ]

        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setFont(btn_font)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            btn.clicked.connect(handler)
            layout.addWidget(btn)

        # === Отступ, чтобы кнопка настроек была внизу ===
        layout.addStretch(1)

        # === Маленькая кнопка настроек в правом нижнем углу ===
        settings_btn = QPushButton("⚙ Настройка COM-порта")
        settings_btn.setFixedHeight(32)
        settings_btn.setStyleSheet("""
            QPushButton {
                font-size: 11px;
                padding: 4px 12px;
            }
        """)
        settings_btn.clicked.connect(self.show_com_port_dialog)
        layout.addWidget(settings_btn, alignment=Qt.AlignmentFlag.AlignRight)

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

    def show_com_port_dialog(self):
        ports_info = list(serial.tools.list_ports.comports())

        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор COM-порта стенда")
        dialog.setMinimumWidth(420)

        layout = QVBoxLayout(dialog)

        if not ports_info:
            layout.addWidget(QLabel(
                "<b>Внимание:</b> Система не видит ни одного COM-порта.<br>"
                "Возможно, стенд не подключён.<br><br>"
                "Вы можете ввести порт вручную (например: <b>COM3</b> или <b>COM5</b>):"
            ))
        else:
            layout.addWidget(QLabel("Выберите COM-порт для подключения к лабораторному стенду:"))

        combo = QComboBox()
        combo.setEditable(True)  # ← обязательно, чтобы можно было ввести вручную

        settings = QSettings("MeasLab", "StandController")
        current_port = settings.value("com_port", "COM3")

        # Заполняем список, если порты есть
        for port in ports_info:
            display_text = f"{port.device} — {port.description}"
            combo.addItem(display_text, port.device)

        # Выбираем текущий сохранённый порт
        index = combo.findData(current_port)
        if index >= 0:
            combo.setCurrentIndex(index)
        else:
            combo.setCurrentText(current_port)

        layout.addWidget(combo)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Берём device из data, либо парсим текст (если ввели вручную)
            selected_device = combo.currentData() or combo.currentText().split(" — ")[0].strip()

            controller = StandController()
            controller.set_port(selected_device)

            QMessageBox.information(
                self,
                "Готово",
                f"COM-порт успешно изменён на <b>{selected_device}</b>.<br><br>"
                "Изменения вступят в силу при следующем подключении к стенду."
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())