# lab5/sub235_window.py
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QTimer
from datetime import datetime
import matplotlib.pyplot as plt

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab5.sub_base import Lab5SubBase
from lab5.lab5_delegate import Lab5Delegate
from utils.tables.read_voltage_button import ReadVoltageButton
from lab5.const_lab5 import R4_VALUES_KOHM
from lab5.calculations_lab5 import calc_ku_theor_iu, calc_ku_exp

COL_R4   = 0
COL_UIN  = 1
COL_UOUT = 2
COL_KT   = 3
COL_KE   = 4
HEADERS  = ["R4, кОм", "Uвх (СКЗ), В", "Uвых (СКЗ), В", "Ku.теор", "Ku.эксп"]


class Sub235Window(Lab5SubBase):
    def __init__(self, controller, parent=None):
        super().__init__("lab5_2.3.5", controller, parent)
        self.start_time = datetime.now()
        self.setWindowTitle("2.3.5 — Исследование ИУ на переменном токе")
        self.resize(580, 280)

        self.table = PasteTableWidget(len(R4_VALUES_KOHM), len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setItemDelegate(Lab5Delegate(self._safe_recalculate, self))

        self.read_uout_btn = ReadVoltageButton(
            self.controller.stand,
            self._set_current_uout,
            label_text="Uвых, В:"
        )

        for i, r4 in enumerate(R4_VALUES_KOHM):
            self._set_fixed(i, COL_R4, str(r4))
            self._set_fixed(i, COL_KT, f"{abs(calc_ku_theor_iu(r4)):.3f}")

        btn_graph = QPushButton("График Ku = F(R4)")
        btn_graph.clicked.connect(self._plot)
        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.5.7(ИУ AC)": self.table})
        )
        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>2.3.5.</b> Исследование ИУ на переменном токе<br>"
            "<small>K<sub>u.теор</sub> = |R4/R1|, R1 = 10 кОм &nbsp;|&nbsp; "
            "K<sub>u.эксп</sub> = U<sub>вых</sub>(СКЗ) / U<sub>вх</sub>(СКЗ)</small>"
        ))
        layout.addWidget(self.table)
        layout.addWidget(self.read_uout_btn)
        hl = QHBoxLayout()
        hl.addWidget(btn_graph)
        hl.addWidget(btn_save)
        layout.addLayout(hl)
        layout.addStretch()
        layout.addWidget(self.timer_label)
        layout.addWidget(btn_exit)

        timer = QTimer(self)
        timer.timeout.connect(
            lambda: update_timer_label(self.start_time, self.timer_label)
        )
        timer.start(1000)
        update_timer_label(self.start_time, self.timer_label)

        self._load_session()

    def _do_recalculate(self):
        for i in range(len(R4_VALUES_KOHM)):
            uin  = self._get_float(i, COL_UIN)
            uout = self._get_float(i, COL_UOUT)
            if uin is not None and uout is not None and uin != 0:
                self._set_calc(i, COL_KE, f"{calc_ku_exp(uout, uin):.4f}")

    def _plot(self):
        r4_t, kt_pts = [], []
        r4_e, ke_pts = [], []
        for i, r4 in enumerate(R4_VALUES_KOHM):
            try:
                kt_pts.append(float(self.table.item(i, COL_KT).text()))
                r4_t.append(r4)
            except (AttributeError, ValueError):
                pass
            try:
                ke_pts.append(float(self.table.item(i, COL_KE).text()))
                r4_e.append(r4)
            except (AttributeError, ValueError):
                pass
        plt.figure(figsize=(9, 5))
        if r4_t: plt.plot(r4_t, kt_pts, "b-",   label="Ku.теор")
        if r4_e: plt.plot(r4_e, ke_pts, "ro--", label="Ku.эксп")
        plt.xlabel("R4, кОм"); plt.ylabel("Ku")
        plt.title("Зависимость Ku ИУ от R4 (переменный ток)")
        plt.legend(); plt.grid(True); plt.tight_layout(); plt.show()

    def _set_current_uout(self, value_v):
        row = self.table.currentRow()
        if row < 0:
            row = 0
        self.table.setItem(row, COL_UOUT, self._editable_item(f"{value_v:.4f}"))
        self._safe_recalculate()

    def _editable_item(self, text):
        from PyQt6.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(text))
