from PySide6.QtGui import QPixmap, QMouseEvent, QPainter, QBrush, QColor
from PySide6.QtWidgets import QVBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt, Signal, QSize

from dataclasses import dataclass
from outlined_label import OutlinedLabel

@dataclass
class TrackInfo:
    track_id: str
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
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.track_info = None
        self.background_pixmap = None
        self.hovered = False  # New flag for hover effect
        self.hover_effect_enabled = True  # Control hover effect
        self.clickable = True  # Control clickability

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

    def sizeHint(self):
        """Return the preferred size (square)"""
        return QSize(400, 400)  # Default square size

    def heightForWidth(self, width):
        """Return height that maintains 1:1 aspect ratio"""
        return width

    def hasHeightForWidth(self):
        """Enable height-for-width geometry management"""
        return True

    def set_hover_effect(self, enabled):
        """Enable or disable the hover effect"""
        self.hover_effect_enabled = enabled

    def set_clickable(self, enabled):
        """Enable or disable clickability"""
        self.clickable = enabled
        # Update cursor based on clickability
        if enabled:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)

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
            # Keep aspect ratio when scaling the image
            scaled_pixmap = self.background_pixmap.scaled(
                widget_rect.size(),
                Qt.KeepAspectRatio,  # Changed from IgnoreAspectRatio
                Qt.SmoothTransformation
            )
            x = (widget_rect.width() - scaled_pixmap.width()) // 2
            y = (widget_rect.height() - scaled_pixmap.height()) // 2
            painter.drawPixmap(x, y, scaled_pixmap)

            if self.hovered and self.hover_effect_enabled:
                painter.fillRect(widget_rect, QColor(0, 0, 0, 50))  # slight dark overlay on hover
        else:
            painter.fillRect(widget_rect, Qt.black)

        super().paintEvent(event)

    def resizeEvent(self, event):
        """Place the label at the bottom 25% and adjust font size proportionally"""
        w, h = self.width(), self.height()
        label_height = int(h * 0.25)
        self.text_label.setGeometry(0, h - label_height, w, label_height)
    
        # Adjust font size based on height
        font = self.text_label.font()
        font.setPointSizeF(h * 0.05)  # 5% of height
        self.text_label.setFont(font)
    
        super().resizeEvent(event)

    def enterEvent(self, event):
        if self.hover_effect_enabled:
            self.hovered = True
            self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.hover_effect_enabled:
            self.hovered = False
            self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton and self.clickable:
            self.clicked.emit()