# lab18/lab18_window.py
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QFrame
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

from utils.excel_timer_helper import update_timer_label
from utils.export_all_to_excel import export_lab_to_excel
from lab18.sub182_window import Sub182Window
from lab18.sub183_window import Sub183Window
from lab18.sub184_window import Sub184Window

_LAB_PREFIX = "lab18_"
_LAB_TITLE  = "Лаб. 18 — Инвертирующий и неинвертирующий сумматор"

_SUB_CLASSES = {
    "182": Sub182Window,
    "183": Sub183Window,
    "184": Sub184Window,
}


class Lab18Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_LAB_TITLE)
        self.resize(490, 320)
        self.start_time = datetime.now()
        self._subs: dict = {}

        title = QLabel(_LAB_TITLE)
        title.setFont(QFont("Calibri", 13, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        grp = QGroupBox("Разделы лабораторной работы")
        g   = QVBoxLayout(grp)
        g.addWidget(self._btn(
            "Исследование инвертирующего сумматора при U_вх1 и U_вх2  в виде постоянных напряжений", "182"))
        g.addWidget(self._btn(
            "Исследование неинвертирующего сумматора при U_вх1 и U_вх2  в виде постоянных напряжений", "183"))
        g.addWidget(self._btn(
            "Исследование неинвертирующего сумматора при U_вх1 в виде синусоидального сигнала", "184"))

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)

        btn_export = QPushButton("📊  Выгрузить все данные в Excel")
        btn_export.setMinimumHeight(40)
        btn_export.setStyleSheet(
            "QPushButton{background:#1F497D;color:white;border-radius:4px;"
            "font-weight:bold;font-size:12px;}"
            "QPushButton:hover{background:#2E6DAD;}"
            "QPushButton:pressed{background:#163A5F;}"
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
        layout.addWidget(grp)
        layout.addWidget(line)
        layout.addWidget(btn_export)
        layout.addLayout(hl)

        tmr = QTimer(self)
        tmr.timeout.connect(lambda: update_timer_label(self.start_time, self.timer_label))
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
                self._subs[key] = cls()
        w = self._subs.get(key)
        if w:
            w.show(); w.raise_(); w.activateWindow()