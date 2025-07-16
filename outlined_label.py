from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QPainter, QPen
from PySide6.QtCore import Qt

# Label to show text with a black border, so that it is easier to display on a white background.
class OutlinedLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.TextAntialiasing)

        # Set font and alignment
        font = self.font()
        text = self.text()
        rect = self.rect()

        # 1. Draw black outline multiple times slightly offset (stroke effect)
        pen = QPen(Qt.black)
        pen.setWidth(2)
        painter.setPen(pen)
        painter.setFont(font)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 4 directions
            painter.drawText(rect.adjusted(dx, dy, dx, dy), self.alignment(), text)

        # 2. Draw white fill text in the center
        painter.setPen(Qt.white)
        painter.drawText(rect, self.alignment(), text)