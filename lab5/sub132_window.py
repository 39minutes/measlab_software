# lab5/sub132_window.py
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import QTimer
from datetime import datetime
import matplotlib.pyplot as plt

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab5.sub_base import Lab5SubBase
from lab5.lab5_delegate import Lab5Delegate
from utils.tables.read_voltage_button import ReadVoltageButton


# Данные из методички
R_VALUES = [float('inf'), 5.0, 3.0, 2.0, 1.0, 0.8, 0.6, 0.4, 0.3, 0.2]
R_LABELS = ["∞", "5", "3", "2", "1", "0.8", "0.6", "0.4", "0.3", "0.2"]

# Строки таблицы
ROW_RN   = 0   # Rн, кОм
ROW_UOUT = 1   # Uвых, В
ROW_IOUT = 2   # Iвых, мА

H_HEADERS = R_LABELS
V_HEADERS = ["Rн, кОм", "Uвых, В", "Iвых, мА"]


class Sub132Window(Lab5SubBase):
    def __init__(self, parent=None):
        super().__init__("lab5_1.3.2", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("1.3.2 — Зависимость Umax(вых) от тока Iвых")
        self.resize(860, 340)

        self.table = PasteTableWidget(3, len(H_HEADERS))
        self.table.setHorizontalHeaderLabels(H_HEADERS)
        self.table.setVerticalHeaderLabels(V_HEADERS)
        self.table.setItemDelegate(Lab5Delegate(self._safe_recalculate, self))

        # Заполняем первую строку — Rн, кОм
        for col, label in enumerate(R_LABELS):
            self._set_fixed(ROW_RN, col, label)

        self.read_uout_btn = ReadVoltageButton(
            self.stand,
            self._fill_selected_uout,
            label_text="Uвых, В:"
        )

        btn_graph = QPushButton("График Uвых = F(Iвых)")
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
        """Iвых (мА) = Uвых / Rн"""
        for col in range(len(R_VALUES)):
            u = self._get_float(ROW_UOUT, col)
            rn = R_VALUES[col]

            if u is not None and rn != 0 and rn != float('inf'):
                i_out = u / rn                     # ← именно Uвых / Rн
                self._set_calc(ROW_IOUT, col, f"{i_out:.3f}")
            else:
                self._set_calc(ROW_IOUT, col, "")

    def _plot(self):
        i_pts, u_pts = [], []
        for col in range(len(R_VALUES)):
            i = self._get_float(ROW_IOUT, col)
            u = self._get_float(ROW_UOUT, col)
            if i is not None and u is not None:
                i_pts.append(i)
                u_pts.append(u)

        plt.figure(figsize=(9, 5))
        if i_pts:
            plt.plot(i_pts, u_pts, "bo-", label="Uвых")
        plt.xlabel("Iвых, мА")
        plt.ylabel("Uвых, В")
        plt.title("Зависимость Umax(вых) от тока Iвых")
        plt.axhline(0, color="k", linewidth=0.5)
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

    def _fill_selected_uout(self, value):
        col = self.table.currentColumn()
        self.table.setItem(ROW_UOUT, col, self._editable_item(f"{value:.3f}"))
        self._safe_recalculate()

    def _editable_item(self, text):
        from PyQt6.QtWidgets import QTableWidgetItem
        return QTableWidgetItem(str(text))