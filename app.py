import sys
from spotify_api import SpotifyAPI

from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, QTimer, Qt 
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QLineEdit,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QListWidgetItem,
    QPushButton, 
    QTreeWidget,
    QTreeWidgetItem,
    QHBoxLayout,
    QListWidget,
    QCheckBox
)

# Main Window SubClass - Main Menu
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("App")
        
        # Variables - Settings/Stored Data
        self.SPOTIFY_API = SpotifyAPI("778df54a97194827a62157c7f785a958", "0129d5e5fabb4c94948d27f3cfa839ad")
        self.ALL_ALBUMS = False                              # Include all albums from the artist
                                                            # TODO: Class that stores an artist, their selected albums and unique songs
        
        self.setMinimumSize(QSize(400, 300))                # Minimum Size
        self.resize(800, 600)                               # Default Size
        
        # Main Container - Will house layouts for search bars, buttons, settings, etc.
        self.container = QWidget()
        self.setCentralWidget(self.container)
        
        main_layout = QVBoxLayout(self.container)
        
        # Search Bar
        self.main_search_bar_text = QLineEdit()
        self.main_search_bar_text.setPlaceholderText("Search for an artist...")
        self.main_search_bar_text.setMaximumHeight(40)
        self.main_search_bar_text.textChanged.connect(self.on_search_text_changed)
        
        # Suggestions List
        self.suggestions_list = QListWidget()
        self.suggestions_list.setMaximumHeight(200)
        self.suggestions_list.hide()                        # Hide when the app is started
        self.suggestions_list.itemClicked.connect(self.on_suggestion_clicked)
        main_layout.addWidget(self.suggestions_list)
        
        # Search Timer to reduce redundant API calls
        self.search_timer = QTimer(self)
        self.search_timer.setInterval(500)                  # 0.5 second cooldown between API calls
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        # Timer Reset
        self.search_cooldown = False
        self.last_search_text = ""
        
        # Tree element to display all songs and artists selected
        self.artist_tree = QTreeWidget(self)
        self.artist_tree.setColumnCount(2)
        self.artist_tree.setHeaderLabels(["Artist", "Remove"])
        self.artist_tree.setColumnWidth(0, 250)
        self.artist_tree.setColumnWidth(1, 40)
        
        # Add top-level artist
        artist_item = QTreeWidgetItem(self.artist_tree)
        artist_item.setText(0, "Artist 1")
        artist_item.setCheckState(0, Qt.Unchecked)

        mic_icon = QIcon("Icons/mic.png")  
        artist_item.setIcon(0, mic_icon)

        trash_icon = QIcon("Icons/trash.png")
        artist_item.setIcon(1, trash_icon)
        
        # Add search bar + suggestions and selected songs to main layout
        main_layout.addWidget(self.main_search_bar_text)
        main_layout.addWidget(self.suggestions_list)
        main_layout.addWidget(self.artist_tree)
        
        main_layout.addStretch()
        
        # Create settings layout 
        settings_layout = QHBoxLayout()
        settings_layout.addStretch()  
        
        # Create and configure checkbox
        self.include_all_albums_checkbox = QCheckBox()
        self.include_all_albums_checkbox.setChecked(self.ALL_ALBUMS)
        self.include_all_albums_checkbox.stateChanged.connect(self.on_include_all_albums_changed)

        self.include_all_albums_label = QLabel("Include All Albums")

        # Add checkbox and label to settings layout
        settings_layout.addWidget(self.include_all_albums_checkbox)
        settings_layout.addWidget(self.include_all_albums_label)
        settings_layout.addStretch()  # Center the checkbox group
        
        # Add settings layout to main layout
        main_layout.addLayout(settings_layout)
        
        # Add stretch to push everything up
        main_layout.addStretch()

    def on_search_text_changed(self, text):
        self.last_search_text = text
        if not self.search_cooldown:
            self.search_timer.start()
            
    # Use the API to get the artist list    
    def perform_search(self):
        text = self.last_search_text.strip()
        if not text:
            self.suggestions_list.clear()
            self.suggestions_list.hide()
            return

        results = self.SPOTIFY_API.search_artists(text)
        results.sort(key=lambda x: x.get("popularity", 0), reverse=True)

        self.suggestions_list.clear()
        for artist in results:
            name = artist.get("name", "Unknown")
            popularity = artist.get("popularity", 0)
            item = QListWidgetItem(f"{name} (Popularity: {popularity})")
            self.suggestions_list.addItem(item)
    
        self.suggestions_list.show()
    
    # Disable the suggestions when you click one
    def on_suggestion_clicked(self, item):
        # Fill the search bar with the clicked artist name
        artist_name = item.text().split(" (Popularity")[0]
        self.main_search_bar_text.blockSignals(True)
        self.main_search_bar_text.setText(artist_name)
        self.main_search_bar_text.blockSignals(False)
        self.suggestions_list.hide()
    
    # CheckBox to Include All albums from artists
    def on_include_all_albums_changed(self, state):
        self.AllAlbums = self.include_all_albums_checkbox.isChecked()
        print(f"All albums will {'be' if self.AllAlbums else 'not be'} included!")
        
# Main code
app = QApplication(sys.argv)
window = MainWindow()
window.show()
        
app.exec()