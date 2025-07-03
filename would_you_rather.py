from PySide6.QtGui import QPixmap
from dataclasses import dataclass

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
            except Exception as e:
                print(f"Error loading image for {self.track_name}: {e}")