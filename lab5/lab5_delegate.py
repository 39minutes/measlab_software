# lab5/lab5_delegate.py
from PyQt6.QtCore import QTimer
from utils.tables.table_validator import NumberDelegate


class Lab5Delegate(NumberDelegate):
    """
    После подтверждения ввода пользователем (Enter/Tab/клик мимо)
    откладывает пересчёт через QTimer.singleShot(0).
    К этому моменту весь C++ стек Qt освободился — рекурсия исключена.
    itemChanged не используется совсем.
    """

    def __init__(self, recalc_callback, parent=None):
        super().__init__(parent)
        self._recalc = recalc_callback

    def setModelData(self, editor, model, index):
        super().setModelData(editor, model, index)
        QTimer.singleShot(0, self._recalc)