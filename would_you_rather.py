from PySide6.QtGui import QPixmap, QMouseEvent, QPainter, QBrush, QColor
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, Signal

from dataclasses import dataclass
from outlined_label import OutlinedLabel

@dataclass
class TrackInfo:
    track_name: str
    artist_name: str
    album_name: str
    release_year: str
    duration: str
    image_url: str
    image_pixmap: QPixmap = None  # To reduce API calls
    
    def __repr__(self):
        return f"{self.track_name}({self.duration}) by {self.artist_name} - {self.album_name}({self.release_year})"
    
    def load_image(self):
        if not self.image_pixmap and self.image_url:
            try:
                from urllib.request import urlopen
                from PySide6.QtCore import QByteArray
                data = urlopen(self.image_url).read()
                self.image_pixmap = QPixmap()
                self.image_pixmap.loadFromData(QByteArray(data))
                return True
            except Exception as e:
                print(f"Error loading image for {self.track_name}: {e}")
        return False
                

class ClickableTrackWidget(QWidget):
    clicked = Signal()  # emits when the widget is clicked

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid transparent;")
        self.image_label.setCursor(Qt.PointingHandCursor)

        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("font-size: 16px; margin-top: 10px;")

        self.layout.addWidget(self.image_label, stretch=8)
        self.layout.addWidget(self.info_label, stretch=1)

class ClickableTrackWidget(QWidget):
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.track_info = None
        self.background_pixmap = None
        self.hovered = False  # New flag for hover effect

        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("border: none;")

        # Label for text at the bottom of the image
        self.text_label = OutlinedLabel(self)
        self.text_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 0.5);
                padding: 8px;
            }
        """)
        self.text_label.setAlignment(Qt.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setAttribute(Qt.WA_TranslucentBackground)
        self.text_label.setAttribute(Qt.WA_TransparentForMouseEvents)  # Clicks go through the label

    def update_track(self, track):
        self.track_info = track
        if track.image_pixmap is None:
            track.load_image()
        self.background_pixmap = track.image_pixmap if track.image_pixmap and not track.image_pixmap.isNull() else None

        self.text_label.setText(f"{track.track_name} ({track.duration}) \n{track.artist_name} \n{track.album_name} ({track.release_year})")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        widget_rect = self.rect()

        if self.background_pixmap:
            scaled_pixmap = self.background_pixmap.scaled(
    widget_rect.size(),
    Qt.IgnoreAspectRatio,
    Qt.SmoothTransformation
)
            x = (widget_rect.width() - scaled_pixmap.width()) // 2
            y = (widget_rect.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)

            if self.hovered:
                painter.fillRect(widget_rect, QColor(0, 0, 0, 50))  # slight dark overlay on hover
        else:
            painter.fillRect(widget_rect, Qt.black)

        super().paintEvent(event)

    def resizeEvent(self, event):
        """Place the label at the bottom 25% of the widget"""
        label_height = int(self.height() * 0.25)
        self.text_label.setGeometry(0, self.height() - label_height, self.width(), label_height)
        super().resizeEvent(event)

    def enterEvent(self, event):
        self.hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
