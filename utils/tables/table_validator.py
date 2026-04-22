from PyQt6.QtWidgets import QStyledItemDelegate, QLineEdit
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator


class NumberDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)

        regex = QRegularExpression(r"-?\d*\.?\d*")
        editor.setValidator(QRegularExpressionValidator(regex, parent))
        return editor

    def setModelData(self, editor, model, index):
        text = editor.text()

        if text == "" or text == ".":
            model.setData(index, "")
        else:
            model.setData(index, text)
