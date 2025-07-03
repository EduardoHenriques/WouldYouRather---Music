
from PySide6.QtCore import QThread, Signal
from spotify_api import SpotifyAPI

class ArtistInfoWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)
    
    def __init__(self, spotify_api: SpotifyAPI, artist_id: str):
        super().__init__()
        self.spotify_api = spotify_api
        self.artist_id = artist_id
        
    def run(self):
        try:
            artist_info = self.spotify_api.get_artist_info(self.artist_id)
            self.finished.emit(artist_info)
        except Exception as e:
            self.error.emit(str(e))