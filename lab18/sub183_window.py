# lab18/sub183_window.py
# 18.3 — Неинвертирующий сумматор при постоянных напряжениях
from datetime import datetime
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDoubleSpinBox, QGroupBox, QTableWidgetItem
)
from PyQt6.QtCore import QTimer

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab18.sub_base18 import Lab18SubBase
from utils.tables.read_voltage_button import ReadVoltageButton
from lab18.calculations_lab18 import calc_uout_noninv


R4_VALUES = [1.0, 2.0, 4.7, 10.0, 20.0, 100.0]

# Строки таблицы
ROW_UOUT_EXP   = 0   # Uвых (эксперимент)
ROW_UOUT_THEOR = 1   # Uвых т (расчёт)

N_ROWS = 2
N_COLS = len(R4_VALUES)

H_HEADERS = ["1", "2", "4,7", "10", "20", "100"]
V_HEADERS = ["Uвых, В", "Uвых т, В"]


class Sub183Window(Lab18SubBase):
    def __init__(self, parent=None):
        super().__init__("lab18_18.3", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("18.3 — Неинвертирующий сумматор")
        self.resize(920, 460)

        # Параметры сверху
        param_grp = QGroupBox("Параметры схемы")
        p_hl = QHBoxLayout(param_grp)

        p_hl.addWidget(QLabel("Uвх1 ="))
        self.u1_spin = QDoubleSpinBox()
        self.u1_spin.setRange(-20.0, 20.0)
        self.u1_spin.setDecimals(3)
        self.u1_spin.setSingleStep(0.1)
        self.u1_spin.setValue(0.4)
        self.u1_spin.valueChanged.connect(self._safe_recalculate)
        p_hl.addWidget(self.u1_spin)
        p_hl.addWidget(QLabel("В   |   Uвх2 ="))

        self.u2_spin = QDoubleSpinBox()
        self.u2_spin.setRange(-20.0, 20.0)
        self.u2_spin.setDecimals(3)
        self.u2_spin.setSingleStep(0.1)
        self.u2_spin.setValue(0.5)
        self.u2_spin.valueChanged.connect(self._safe_recalculate)
        p_hl.addWidget(self.u2_spin)
        p_hl.addWidget(QLabel("В"))
        p_hl.addStretch()

        # Таблица
        self.table = PasteTableWidget(N_ROWS, N_COLS)
        self.table.setHorizontalHeaderLabels(H_HEADERS)
        self.table.setVerticalHeaderLabels(V_HEADERS)

        self.read_uout_btn = ReadVoltageButton(
            self.stand,
            self._set_current_uout,
            label_text="Uвых, В:"
        )

        note = QLabel(
            "<small>Столбцы соответствуют R4, кОм.<br>"
            "<b>Uвх1</b> и <b>Uвх2</b> задаются сверху и заполняются автоматически.<br>"
            "<b>Uвых т</b> рассчитывается автоматически.</small>"
        )
        note.setWordWrap(True)

        btn_plot = QPushButton("График Uвых = f(R4)")
        btn_plot.clicked.connect(self._plot)

        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(self, {"Табл.2.10 Неинв.Сумматор": self.table})
        )

        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Таблица 2.10.</b> Результаты эксперимента схемы неинвертирующего сумматора "
            "при постоянных напряжениях на входах"
        ))
        layout.addWidget(param_grp)
        layout.addWidget(note)
        layout.addWidget(self.table)
        layout.addWidget(self.read_uout_btn)

        hl = QHBoxLayout()
        hl.addWidget(btn_plot)
        hl.addWidget(btn_save)
        layout.addLayout(hl)

        layout.addStretch()
        layout.addWidget(self.timer_label)
        layout.addWidget(btn_exit)

        tmr = QTimer(self)
        tmr.timeout.connect(lambda: update_timer_label(self.start_time, self.timer_label))
        tmr.start(1000)
        update_timer_label(self.start_time, self.timer_label)

        self._load_session()
        self._safe_recalculate()

    def _do_recalculate(self):
        u1 = self.u1_spin.value()
        u2 = self.u2_spin.value()

        for col, r4 in enumerate(R4_VALUES):
            # Расчёт Uвых теоретический (неинвертирующий)
            uout_theor = calc_uout_noninv(r4, u1, u2)
            self._set_calc(ROW_UOUT_THEOR, col, uout_theor)

    def _plot(self):
        r4_vals = R4_VALUES[:]
        u_theor = []
        u_exp = []

        for col in range(N_COLS):
            u_theor.append(self._get_float(ROW_UOUT_THEOR, col) or 0.0)
            ue = self._get_float(ROW_UOUT_EXP, col)
            if ue is not None:
                u_exp.append(ue)

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(r4_vals, u_theor, "b-o", label="Uвых т")
        if len(u_exp) == len(r4_vals):
            ax.plot(r4_vals, u_exp, "rs--", label="Uвых")

        ax.set_xlabel("R4, кОм")
        ax.set_ylabel("Uвых, В")
        ax.set_title("18.3 — Неинвертирующий сумматор: Uвых = f(R4)")
        ax.legend()
        ax.grid(True)
        plt.tight_layout()
        plt.show()

    def _set_current_uout(self, value_v):
        col = self.table.currentColumn()
        if col < 0:
            col = 0
        self.table.setItem(ROW_UOUT_EXP, col, self._editable_item(value_v))
        self._safe_recalculate()

    def _editable_item(self, text):
        """Округление до сотых"""
        try:
            num = float(text)
            return QTableWidgetItem(f"{num:.2f}")
        except (ValueError, TypeError):
            return QTableWidgetItem(str(text))