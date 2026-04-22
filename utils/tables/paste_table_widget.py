from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtGui import QKeyEvent, QKeySequence
import pyperclip
import re


class PasteTableWidget(QTableWidget):
    def keyPressEvent(self, event: QKeyEvent):
        if event.matches(QKeySequence.StandardKey.Paste):
            self.paste_from_clipboard()
        else:
            super().keyPressEvent(event)

    def paste_from_clipboard(self):
        text = pyperclip.paste()
        rows = text.strip().split('\n')
        start_row = self.currentRow()
        start_col = self.currentColumn()

        num_re = re.compile(r'^-?(?:\d+(?:\.\d*)?|\.\d+)$')

        for dr, row_data in enumerate(rows):
            cols = row_data.split('\t')
            for dc, cell in enumerate(cols):
                r = start_row + dr
                c = start_col + dc
                if r >= self.rowCount() or c >= self.columnCount():
                    continue

                s = cell.strip()

                if num_re.match(s):
                    self.setItem(r, c, QTableWidgetItem(s))
