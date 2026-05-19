# lab16_17/lab1617_window.py
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QGroupBox, QFrame
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

from utils.excel_timer_helper import update_timer_label
from utils.export_all_to_excel import export_lab_to_excel

# Остался только один sub-окно
from lab16_17.sub1653_window import Sub1653Window

_LAB_PREFIX = "lab1617_"
_LAB_TITLE  = "Исследование дифференциального операционного усилителя"

_SUB_CLASSES = {
    "1653": Sub1653Window,
    # 1654 полностью удалён
}


class Lab1617Window(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(_LAB_TITLE)
        self.resize(460, 220)          # окно стало меньше
        self.start_time = datetime.now()
        self._subs: dict[str, QWidget] = {}

        title = QLabel(_LAB_TITLE)
        title.setFont(QFont("Calibri", 13, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        grp = QGroupBox("Разделы лабораторной работы")
        g = QVBoxLayout(grp)
        g.addWidget(self._btn(
            "Исследование дифференциального усилителя", "1653"))

        # Кнопка 16.5.4 удалена

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
                self._subs[key] = cls()
        w = self._subs.get(key)
        if w:
            w.show()
            w.raise_()
            w.activateWindow()