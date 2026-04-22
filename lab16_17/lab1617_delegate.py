# lab16_17/lab1617_delegate.py
from PyQt6.QtCore import QTimer
from utils.tables.table_validator import NumberDelegate


class Lab1617Delegate(NumberDelegate):
    def __init__(self, recalc_callback, parent=None):
        super().__init__(parent)
        self._recalc = recalc_callback

    def setModelData(self, editor, model, index):
        super().setModelData(editor, model, index)
        QTimer.singleShot(0, self._recalc)