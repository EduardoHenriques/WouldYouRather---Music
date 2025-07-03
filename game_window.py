from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from spotify_api import SpotifyAPI
import random


class GameWindow(QMainWindow):
    def __init__(self, selected_items=None, spotify_api=None, return_to_main_callback=None):
        super().__init__()
        self.setWindowTitle("Music Game")
        self.setMinimumSize(QSize(800, 400))
        self.resize(1000, 600)

        self.api = spotify_api                      # None if not in endless mode
        self.selected_items = selected_items or []  # Empty list if not provided
        self.return_to_main_callback = return_to_main_callback

        # UI setup
        self.container = QWidget()
        self.setCentralWidget(self.container)
        main_layout = QVBoxLayout(self.container)

        title_label = QLabel("Choose Your Favorite!")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        main_layout.addWidget(title_label)

        game_layout = QHBoxLayout()
        self.left_button = QPushButton()
        self.right_button = QPushButton()

        for button, side in [(self.left_button, "left"), (self.right_button, "right")]:
            button.setMinimumHeight(200)
            button.setStyleSheet(self.button_style())
            button.clicked.connect(lambda _, s=side: self.on_choice_made(s))
            game_layout.addWidget(button)

        main_layout.addLayout(game_layout)

        # Control buttons
        control_layout = QHBoxLayout()
        self.new_round_button = QPushButton("New Round")
        self.new_round_button.clicked.connect(self.start_new_round)

        self.back_button = QPushButton("Back to Main")
        self.back_button.clicked.connect(self.go_back_to_main)

        control_layout.addWidget(self.new_round_button)
        control_layout.addWidget(self.back_button)
        main_layout.addLayout(control_layout)

        # Start game logic depending on mode
        self.start_new_round()

    def button_style(self):
        return """
            QPushButton {
                font-size: 16px;
                padding: 20px;
                border: 2px solid #ccc;
                border-radius: 10px;
                background-color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #999;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """

    def start_new_round(self):
        if len(self.selected_items) < 2:
            QMessageBox.warning(self, "Not Enough Items",
                                "You need at least 2 items selected to play the game!")
            return
        
        self.current_pair = random.sample(self.selected_items, 2)
        self.left_button.setText(self.format_item_text(self.current_pair[0]))
        self.right_button.setText(self.format_item_text(self.current_pair[1]))

    def format_item_text(self, item):
        return f"{item.artist_name}\n\n{item.album_name}\n\n{item.track_name}"

    def on_choice_made(self, choice):
        chosen_item = self.current_pair[0] if choice == "left" else self.current_pair[1]
        print(f"User chose: {chosen_item.track_name} by {chosen_item.artist_name}")
        self.start_new_round()

    def go_back_to_main(self):
        self.close()
        self.return_to_main_callback()