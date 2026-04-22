# lab5/sub132_window.py
from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import QTimer
from datetime import datetime
import matplotlib.pyplot as plt

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab5.sub_base import Lab5SubBase
from lab5.lab5_delegate import Lab5Delegate
from lab5.const_lab5 import RN_VALUES_KOHM, RN_LABELS

COL_RN = 0
COL_UP = 1
COL_IP = 2
COL_UM = 3
COL_IM = 4
HEADERS = ["Rн, кОм", "Uвых+, В", "Iвых+, мА", "Uвых-, В", "Iвых-, мА"]


class Sub132Window(Lab5SubBase):
    def __init__(self, controller, parent=None):
        super().__init__("lab5_1.3.2", controller, parent)
        self.start_time = datetime.now()
        self.setWindowTitle("1.3.2 — Зависимость Umax(вых) от тока Iвых")
        self.resize(600, 380)

        self.table = PasteTableWidget(len(RN_VALUES_KOHM), len(HEADERS))
        self.table.setHorizontalHeaderLabels(HEADERS)
        self.table.setItemDelegate(Lab5Delegate(self._safe_recalculate, self))

        for i, lbl in enumerate(RN_LABELS):
            self._set_fixed(i, COL_RN, lbl)

        btn_graph = QPushButton("График  Uвых = F(Iвых)")
        btn_graph.clicked.connect(self._plot)
        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.5.4": self.table})
        )
        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Таблица 5.4.</b> Зависимость U<sub>вых</sub>(макс) от тока I<sub>вых</sub><br>"
            "<small>I<sub>вых</sub> (мА) = |U<sub>вых</sub>| / R<sub>н</sub> — рассчитывается автоматически</small>"
        ))
        layout.addWidget(self.table)
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
        for i, rn in enumerate(RN_VALUES_KOHM):
            for u_col, i_col in ((COL_UP, COL_IP), (COL_UM, COL_IM)):
                u = self._get_float(i, u_col)
                if u is not None:
                    self._set_calc(i, i_col,
                                   f"{self.controller.compute_i_out(abs(u), rn):.3f}")

    def _plot(self):
        pos_pts, neg_pts = [], []
        for i in range(len(RN_VALUES_KOHM)):
            ip = self._get_float(i, COL_IP); up = self._get_float(i, COL_UP)
            im = self._get_float(i, COL_IM); um = self._get_float(i, COL_UM)
            if ip is not None and up is not None:
                pos_pts.append((ip, up))
            if im is not None and um is not None:
                neg_pts.append((im, abs(um)))
        plt.figure(figsize=(9, 5))
        if pos_pts:
            xs, ys = zip(*sorted(pos_pts))
            plt.plot(xs, ys, "bo-", label="+Uвых")
        if neg_pts:
            xs, ys = zip(*sorted(neg_pts))
            plt.plot(xs, [-v for v in ys], "rs--", label="−Uвых")
        plt.xlabel("Iвых, мА"); plt.ylabel("Uвых, В")
        plt.title("Зависимость Umax(вых) от тока Iвых")
        plt.axhline(0, color="k", linewidth=0.5)
        plt.legend(); plt.grid(True); plt.tight_layout(); plt.show()