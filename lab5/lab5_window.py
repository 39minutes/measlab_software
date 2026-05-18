# lab5/lab5_window.py
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QFrame
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

from utils.excel_timer_helper import update_timer_label
from utils.export_all_to_excel import export_lab_to_excel
from lab5.controller_lab5 import Lab5Controller
from lab5.sub131_window import Sub131Window
from lab5.sub132_window import Sub132Window
from lab5.sub133_window import Sub133Window
from lab5.sub231_window import Sub231Window
from lab5.sub232_window import Sub232Window
from lab5.sub233_window import Sub233Window
from lab5.sub234_window import Sub234Window
from lab5.sub235_window import Sub235Window

_LAB_PREFIX = "lab5_"
_LAB_TITLE  = "Лаб. 5 — Операционные усилители"

_SUB_CLASSES = {
    "131": Sub131Window,
    "132": Sub132Window,
    "133": Sub133Window,
    "231": Sub231Window,
    "232": Sub232Window,
    "233": Sub233Window,
    "234": Sub234Window,
    "235": Sub235Window,
}


class Lab5Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_LAB_TITLE)
        self.resize(500, 480)
        self.start_time = datetime.now()
        self.controller = Lab5Controller()
        self._subs: dict[str, QWidget] = {}

        title = QLabel(_LAB_TITLE)
        title.setFont(QFont("Calibri", 13, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        grp1 = QGroupBox("Часть 1. Основные характеристики ОУ")
        g1   = QVBoxLayout(grp1)
        g1.addWidget(self._btn("Снятие передаточной характеристики ОУ на постоянном токе",          "131"))
        g1.addWidget(self._btn("Определение зависимости максимального положительного и отрицательного выходного напряжения ОУ от выходного тока",      "132"))
        g1.addWidget(self._btn("Измерение значения напряжения смещения ОУ",                  "133"))

        grp2 = QGroupBox("Часть 2. Усилители на ОУ")
        g2   = QVBoxLayout(grp2)
        g2.addWidget(self._btn("Зависимость коэффициента усиления НУ от сопротивления R4",                 "231"))
        g2.addWidget(self._btn("Передаточная характеристика НУ на постоянном токе",          "232"))
        g2.addWidget(self._btn("Передаточная характеристика повторителя напряжения", "233"))
        g2.addWidget(self._btn("Передаточная характеристика ИУ на постоянном токе",      "234"))
        g2.addWidget(self._btn("Исследование ИУ на переменном токе",      "235"))

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)

        btn_export = QPushButton("📊  Выгрузить все данные в Excel")
        btn_export.setMinimumHeight(40)
        btn_export.setToolTip(
            "Экспортирует данные ВСЕХ подпунктов лабораторной в один файл Excel.\n"
            "Данные автоматически сохраняются при закрытии каждого подокна.\n"
            "Каждый подпункт — отдельный лист."
        )
        btn_export.setStyleSheet(
            "QPushButton {"
            "  background-color:#1F497D; color:white;"
            "  border-radius:4px; font-weight:bold; font-size:12px;"
            "}"
            "QPushButton:hover   { background-color:#2E6DAD; }"
            "QPushButton:pressed { background-color:#163A5F; }"
        )
        btn_export.clicked.connect(
            lambda: export_lab_to_excel(self, _LAB_PREFIX, _LAB_TITLE)
        )

        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)
        hl = QHBoxLayout()
        hl.addWidget(self.timer_label)
        hl.addStretch()
        hl.addWidget(btn_exit)

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.addWidget(title)
        layout.addWidget(grp1)
        layout.addWidget(grp2)
        layout.addWidget(line)
        layout.addWidget(btn_export)
        layout.addLayout(hl)

        tmr = QTimer(self)
        tmr.timeout.connect(
            lambda: update_timer_label(self.start_time, self.timer_label)
        )
        tmr.start(1000)
        update_timer_label(self.start_time, self.timer_label)

    def _btn(self, label: str, key: str) -> QPushButton:
        b = QPushButton(label)
        b.clicked.connect(lambda: self._open(key))
        return b

    def _open(self, key: str):
        if key not in self._subs:
            cls = _SUB_CLASSES.get(key)
            if cls:
                self._subs[key] = cls(self.controller)
        w = self._subs.get(key)
        if w:
            w.show()
            w.raise_()
            w.activateWindow()