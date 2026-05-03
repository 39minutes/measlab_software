# lab16_17/sub1654_window.py
from datetime import datetime
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QPushButton
)
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QTableWidgetItem

from utils.tables.paste_table_widget import PasteTableWidget
from utils.excel_timer_helper import update_timer_label, export_tables_to_excel
from lab16_17.sub_base1617 import Lab1617SubBase
from lab16_17.lab1617_delegate import Lab1617Delegate
from utils.tables.read_voltage_button import ReadVoltageButton
from lab16_17.calculations_lab1617 import calc_ku_inv


R4_VALUES = [1.0, 2.0, 4.7, 10.0, 20.0, 100.0]

ROW_R4 = 0
ROW_UOUT = 1
ROW_KU_THEOR = 2
ROW_KU_EXP = 3

COL_LABEL = 0
COL_DATA_START = 1

N_ROWS = 4
N_COLS = 7


class Sub1654Window(Lab1617SubBase):
    def __init__(self, parent=None):
        super().__init__("lab1617_16.5.4", parent)
        self.start_time = datetime.now()
        self.setWindowTitle("16.5.4 — Инвертирующий усилитель")
        self.resize(820, 420)

        self.table = PasteTableWidget(N_ROWS, N_COLS)
        self.table.setItemDelegate(Lab1617Delegate(self._safe_recalculate, self))
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(False)

        self._init_table()

        self.read_uout_btn = ReadVoltageButton(
            self.stand,
            self._set_current_uout,
            label_text="Uвых, В:"
        )

        note = QLabel(
            "<small>Таблица повторяет рисунок 1 в 1: по столбцам задаются значения "
            "R4, в строку <b>Uвых, В</b> заносятся экспериментальные данные, "
            "строки <b>Ku теор</b> и <b>Ku эксп</b> рассчитываются автоматически.</small>"
        )
        note.setWordWrap(True)

        btn_plot = QPushButton("График Uвых = f(R4)")
        btn_plot.clicked.connect(self._plot)

        btn_save = QPushButton("Сохранить в Excel")
        btn_save.clicked.connect(
            lambda: export_tables_to_excel(
                self, {"Табл.16.5.4 ИнвУс": self.table}
            )
        )

        self.timer_label = QLabel()
        btn_exit = QPushButton("Закрыть")
        btn_exit.clicked.connect(self.close)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "<b>Зависимость выходного напряжения от сопротивления обратной связи "
            "неинвертирующего усилителя</b>"
        ))
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

    def _init_table(self):
        self._set_fixed(ROW_R4, COL_LABEL, "R4, кОм")
        self._set_fixed(ROW_UOUT, COL_LABEL, "Uвых, В")
        self._set_fixed(ROW_KU_THEOR, COL_LABEL, "Ku теор")
        self._set_fixed(ROW_KU_EXP, COL_LABEL, "Ku эксп")

        for i, r4 in enumerate(R4_VALUES, start=COL_DATA_START):
            self._set_fixed(ROW_R4, i, self._format_r4(r4))

    def _format_r4(self, value):
        if abs(value - round(value)) < 1e-9:
            return str(int(round(value)))
        return str(value).replace(".", ",")

    def _do_recalculate(self):
        for i, r4 in enumerate(R4_VALUES, start=COL_DATA_START):
            ku_theor = calc_ku_inv(r4, 1.0)
            self._set_calc(ROW_KU_THEOR, i, f"{abs(ku_theor):.4f}")

            uout = self._get_float(ROW_UOUT, i)
            if uout is not None:
                self._set_calc(ROW_KU_EXP, i, f"{abs(uout):.4f}")
            else:
                self._set_calc(ROW_KU_EXP, i, "")

    def _plot(self):
        r4_vals = []
        uout_vals = []

        for i, r4 in enumerate(R4_VALUES, start=COL_DATA_START):
            uout = self._get_float(ROW_UOUT, i)
            if uout is not None:
                r4_vals.append(r4)
                uout_vals.append(uout)

        if not r4_vals:
            return

        fig, ax = plt.subplots(figsize=(9, 5))
        ax.plot(r4_vals, uout_vals, "bo-", label="Uвых эксп")
        ax.set_xlabel("R4, кОм")
        ax.set_ylabel("Uвых, В")
        ax.set_title("Зависимость выходного напряжения от сопротивления обратной связи")
        ax.grid(True)
        ax.legend()
        plt.tight_layout()
        plt.show()

    def _set_current_uout(self, value_v):
        col = self.table.currentColumn()
        if col < COL_DATA_START:
            col = COL_DATA_START
        self.table.setItem(ROW_UOUT, col, self._editable_item(f"{value_v:.4f}"))
        self._safe_recalculate()

    def _editable_item(self, text):
        return QTableWidgetItem(str(text))