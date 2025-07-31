import sys, random
from spotify_api import SpotifyAPI
from artist_worker import ArtistInfoWorker
from game_window import GameWindow
from would_you_rather import TrackInfo


from PySide6.QtGui import QIcon
from PySide6.QtCore import QSize, QTimer, Qt 
from PySide6.QtWidgets import (
    QApplication,
    QLineEdit,
    QSizePolicy,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox,
    QProgressBar,
    QTreeWidget,
    QTreeWidgetItem,
    QHBoxLayout,
    QListWidget,
    QCheckBox
)

##############################################################################################################
####                                                                                                      ####
##############################################################################################################

# Main Window SubClass - Main Menu
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set icon for application
        app_icon = QIcon("Icons/AppIcon.ico")
        self.setWindowIcon(app_icon)
        QApplication.setWindowIcon(app_icon)
        # Set Window Title
        self.setWindowTitle("Would You Rather - Music")
        

        
        # Variables - Settings/Stored Data
        self.SPOTIFY_API = SpotifyAPI("778df54a97194827a62157c7f785a958", "0129d5e5fabb4c94948d27f3cfa839ad")
        self.ALL_ALBUMS = False                              # Include all albums from the artist
        
        self.setMinimumSize(QSize(400, 300))                # Minimum Size
        self.resize(800, 600)                               # Default Size
        
        self.artist_worker = None
        
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
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)
        
        
        # Tree element to display all songs and artists selected
        self.artist_tree = QTreeWidget(self)
        self.artist_tree.setColumnCount(2)
        self.artist_tree.setHeaderLabels(["Artist", "Remove"])
        self.artist_tree.setColumnWidth(0, 250)
        self.artist_tree.setColumnWidth(1, 40)
        self.artist_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        
        self.artist_tree.itemChanged.connect(self.on_item_check_state_changed)
        
        # Start Button
        self.start_button = QPushButton()
        self.start_button.setText("Start Game")
        self.start_button.clicked.connect(self.start_game)
        
        # Endless Mode Check
        self.endless_mode = QCheckBox()
        self.endless_mode.setChecked(False)
        self.endless_mode.setText("Endless Mode(Random Artists/Songs)")
        
        # Add search bar + suggestions and the tree to select artists/tracks to main layout
        main_layout.addWidget(self.main_search_bar_text)
        main_layout.addWidget(self.suggestions_list)
        main_layout.addWidget(self.artist_tree, stretch=1)
        main_layout.addStretch()
        
        # Create settings layout 
        settings_layout = QHBoxLayout()
        settings_layout.addWidget(self.start_button)
        settings_layout.addWidget(self.endless_mode)
        
        main_layout.addLayout(settings_layout)
    
    
    #############################################################################################
    ####                                                                                     ####
    #############################################################################################
    
    def start_game(self):
        """Start a normal game with the selected tracks or an endless game"""
    
        if self.endless_mode.isChecked():
            # ✅ Endless Mode: Create game with 3 random tracks
            self.game_window = GameWindow(
                selected_items=[self.SPOTIFY_API.endless_mode() for _ in range(3)],
                spotify_api=self.SPOTIFY_API,
                return_to_main_callback=self.show_main_window
            )
            self.game_window.show()
            self.close()
            return  # ✅ Prevent execution of normal mode logic
    
        # ✅ Normal Mode
        print("Normal Gaming")
        selected_items = self.get_selected_items()
    
        if not selected_items or len(selected_items) < 2:
            QMessageBox.warning(self, "No Selection",
                                "Please select at least 2 tracks to start the game!")
            return
    
        self.game_window = GameWindow(
            selected_items=selected_items,
            spotify_api=None,
            return_to_main_callback=self.show_main_window
        )
        self.game_window.show()
        self.close()
    
    def on_search_text_changed(self, text):
        self.last_search_text = text
        if not self.search_cooldown:
            self.search_timer.start()
            
    def get_selected_items(self):
        """Get all selected items from the tree and store them as TrackInfo objects"""
        selected_items = []

        # Iterate through all top-level items (artists)
        for i in range(self.artist_tree.topLevelItemCount()):
            artist_item = self.artist_tree.topLevelItem(i)
            artist_name = artist_item.text(0)

            # Iterate through albums
            for j in range(artist_item.childCount()):
                album_item = artist_item.child(j)
                album_name = album_item.text(0)
                album_year = album_item.text(1)
                cover_url = album_item.data(0, Qt.UserRole) 

                # Iterate through tracks
                for k in range(album_item.childCount()):
                    track_item = album_item.child(k)

                    if track_item.checkState(0) == Qt.Checked:
                        track_name = track_item.text(0)
                        duration = track_item.text(2)

                        selected_items.append(
                        TrackInfo(
                            track_id=None,
                            track_name=track_name,
                            artist_name=artist_name,
                            album_name=album_name,
                            release_year=album_year,
                            duration=duration,
                            image_url=cover_url
                        )
                        )

        return selected_items  
         
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
            item = QListWidgetItem(f"{name}")
            item.setData(Qt.UserRole, artist)
            self.suggestions_list.addItem(item)
    
        self.suggestions_list.show()
    
    # Disable the suggestions when you click one
    def on_suggestion_clicked(self, item):
        artist_data = item.data(Qt.UserRole)  # Retrieve stored dict

        if artist_data:
            artist_name = artist_data.get("name", "Unknown")
            artist_id = artist_data.get("id", None)
            
            self.main_search_bar_text.blockSignals(True)
            self.main_search_bar_text.setText(artist_name)
            self.main_search_bar_text.blockSignals(False)
            self.suggestions_list.hide()

            self.progress_bar.show()
            
            self.worker = ArtistInfoWorker(self.SPOTIFY_API, artist_id)
            self.worker.finished.connect(self.on_artist_info_received)
            self.worker.error.connect(self.on_artist_info_error)
            self.worker.start()
            
                 
    def on_artist_info_received(self, artist_data):
        """Called when artist info is successfully loaded"""
        self.progress_bar.hide()
        self.populate_artist_tree(self.artist_tree, artist_data)
        
    def on_artist_info_error(self, error_message):
        """Called when there's an error loading artist info"""
        print("Error..." + error_message)
        self.progress_bar.hide()
    
    # CheckBox to Include All albums from artists
    def on_include_all_albums_changed(self, state):
        self.AllAlbums = self.include_all_albums_checkbox.isChecked()
        print(f"All albums will {'be' if self.AllAlbums else 'not be'} included!")
        
    def populate_artist_tree(self, artist_tree, artist_data):
        # Set up tree with 4 columns: Name, Year, Duration, Remove
        artist_tree.setUpdatesEnabled(False)
        artist_tree.setColumnCount(4)
        artist_tree.setHeaderLabels(["Name", "Year", "Duration", "Remove"])
        artist_tree.setColumnWidth(0, 250)  # Name
        artist_tree.setColumnWidth(1, 60)   # Year
        artist_tree.setColumnWidth(2, 70)   # Duration
        artist_tree.setColumnWidth(3, 40)   # Remove

        # Icons
        mic_icon = QIcon("Icons/mic.png")
        trash_icon = QIcon("Icons/trash.png")
        album_icon = QIcon("Icons/album.png")
        track_icon = QIcon("Icons/music.png")

        # Create artist item
        artist_item = QTreeWidgetItem(artist_tree)
        artist_item.setText(0, artist_data.get("artist_name", "Unknown"))
        artist_item.setCheckState(0, Qt.Unchecked)
        artist_item.setIcon(0, mic_icon)
        artist_item.setIcon(3, trash_icon)  # Move trash icon to 4th column
        artist_item.setData(0, Qt.UserRole, artist_data["artist_id"])

        # Sort albums by year descending, then by name ascending
        albums = []
        for album_name, album_info in artist_data["albums"].items():
            try:
                year = int(album_info["year"]) if album_info["year"].isdigit() else 0
            except (TypeError, ValueError):
                year = 0
            albums.append((year, album_name, album_info))
        albums.sort(key=lambda x: (-x[0], x[1]))

        # Add albums and tracks
        for year, album_name, album_info in albums:
            album_item = QTreeWidgetItem(artist_item)
            album_item.setText(0, album_name)
            album_item.setText(1, album_info["year"])
            album_item.setCheckState(0, Qt.Unchecked)
            album_item.setIcon(0, album_icon)
            album_item.setIcon(3, trash_icon)
            cover_url = album_info.get("cover_url", "")
            album_item.setData(0, Qt.UserRole, cover_url)

            for track_name, track_data in album_info["tracks"].items():
                duration = track_data.get("duration", "")
                track_item = QTreeWidgetItem(album_item)
                track_item.setText(0, track_name)
                track_item.setText(2, duration)  # Duration in 3rd column (index 2)
                track_item.setCheckState(0, Qt.Unchecked)
                track_item.setIcon(0, track_icon)
                track_item.setIcon(3, trash_icon)

        artist_tree.setUpdatesEnabled(True)

    # Tree propagation properties
    def on_item_check_state_changed(self, item, column):
        if column != 0:
            return  # Only process for first column (with checkboxes)

        state = item.checkState(0)

        # Block signal temporarily to avoid recursion
        self.artist_tree.blockSignals(True)

        # Propagate downwards
        self.propagate_check_state_to_children(item, state)

        # Propagate upwards
        if state == Qt.Checked:
            self.propagate_check_state_to_parents(item)

        self.artist_tree.blockSignals(False)   
           
    def propagate_check_state_to_children(self, item, state):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self.propagate_check_state_to_children(child, state)
    
    def propagate_check_state_to_parents(self, item):
        parent = item.parent()
        if parent and parent.checkState(0) != Qt.Checked:
            parent.setCheckState(0, Qt.Checked)
            self.propagate_check_state_to_parents(parent)
            
    def show_main_window(self):
        self.show()
        
    
