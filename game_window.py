from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from spotify_api import SpotifyAPI
from outlined_label import OutlinedLabel
from would_you_rather import ClickableTrackWidget
import random


class GameWindow(QMainWindow):
    def __init__(self, selected_items=None, spotify_api: SpotifyAPI =None, return_to_main_callback=None):
        super().__init__()
        self.setWindowTitle("Music Game")
        self.setMinimumSize(QSize(800, 400))
        self.resize(1000, 600)

        self.api = spotify_api                      # None if not in endless mode
        self.selected_items = selected_items or []  # Empty list if not provided
        self.return_to_main_callback = return_to_main_callback
        
        self.current_challenger = None              # When the game starts, there is no current challenger as no song has won a match

        # Set a dark background for the main window
        self.setStyleSheet("""
        ClickableTrackWidget {
            border: 4px solid transparent;
            border-radius: 15px;
            background-color: rgba(0, 0, 0, 0.3);
        }
        ClickableTrackWidget:hover {
            border: 4px solid #FFD700;
            background-color: rgba(255, 255, 255, 0.1);
        }
        """)

        # UI setup
        self.container = QWidget()
        self.setCentralWidget(self.container)
        main_layout = QVBoxLayout(self.container)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins for full background effect

        # Title with improved styling
        title_label = QLabel("Choose Your Favorite!")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                font-size: 32px; 
                font-weight: bold; 
                color: white;
                background-color: rgba(0, 0, 0, 0.8);
                padding: 20px;
                border-radius: 10px;
                margin: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Game Layout - Two halves, each one with the album cover as background
        game_layout = QHBoxLayout()
        game_layout.setContentsMargins(0, 0, 0, 0)
        game_layout.setSpacing(0)  # No spacing between the two halves
        
        self.left_widget = ClickableTrackWidget()
        self.right_widget = ClickableTrackWidget()

        self.left_widget.clicked.connect(lambda: self.on_choice_made("left"))
        self.right_widget.clicked.connect(lambda: self.on_choice_made("right"))
        
        vs_label = QLabel("VS")
        vs_label.setAlignment(Qt.AlignCenter)
        vs_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 48px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        
                
        game_layout.addWidget(self.left_widget, stretch=1)
        # game_layout.addWidget(vs_label, stretch=1)
        game_layout.addWidget(self.right_widget, stretch=1)

        main_layout.addLayout(game_layout, stretch=1)  # Give most space to the game area

        # Control buttons with improved styling
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(20, 10, 20, 10)
        
        self.new_round_button = QPushButton("New Round")
        self.new_round_button.clicked.connect(self.start_new_round)
        self.new_round_button.setStyleSheet(self.button_style())

        self.back_button = QPushButton("Back to Main")
        self.back_button.clicked.connect(self.go_back_to_main)
        self.back_button.setStyleSheet(self.button_style())

        control_layout.addWidget(self.new_round_button)
        control_layout.addWidget(self.back_button)
        main_layout.addLayout(control_layout)

        # Check if we have enough items before starting the game
        if len(self.selected_items) >= 2:
            self.start_new_round(first_round=True)
        else:
            # Show placeholder content or disable the game
            self.show_not_enough_items_message()
        
    def show_not_enough_items_message(self):
        """Show a message when there aren't enough items to start the game"""
        # You can customize this to show a better message in the game area
        placeholder_label = QLabel("Not enough items selected to start the game!")
        placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                background-color: rgba(255, 0, 0, 0.3);
                padding: 20px;
                border-radius: 10px;
            }
        """)
        # You might want to add this to your layout or handle it differently
        
    def button_style(self):
        return """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 15px 30px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
                border-color: rgba(255, 255, 255, 0.6);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """
        
        
    def start_new_round(self, first_round=False):
        # Only check for items if it's not the first round
        # (first round check is done in __init__)
        if not first_round and len(self.selected_items) < 2:
            QMessageBox.warning(self, "Not Enough Items",
                                "You need at least 2 items selected to play the game!")
            return

        # First round: pick two random songs
        if first_round or not self.current_challenger:
            self.current_pair = random.sample(self.selected_items, 2)
            self.current_challenger = self.current_pair[0]  # default challenger
        else:
            # Challenger stays, pick a new random opponent
            available = [item for item in self.selected_items if item != self.current_challenger]
            if not available:
                QMessageBox.information(self, "Game Over", "No more unique challengers left!")
                return
            new_opponent = random.choice(available)
            # New challenger goes on the left
            self.current_pair = [self.current_challenger, new_opponent]

        # Always update both widgets
        self.left_widget.update_track(self.current_pair[0])
        self.right_widget.update_track(self.current_pair[1])

    def format_item_text(self, item):
        return f"{item.artist_name}\n\n{item.album_name}\n\n{item.track_name}"

    def on_choice_made(self, choice):
        chosen_item = self.current_pair[0] if choice == "left" else self.current_pair[1]
        print(f"User chose: {chosen_item.track_name} by {chosen_item.artist_name}")
        self.current_challenger = chosen_item  # <-- update challenger
        self.start_new_round()
        
    def go_back_to_main(self):
        self.close()
        self.return_to_main_callback()