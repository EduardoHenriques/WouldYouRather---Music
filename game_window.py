from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QMessageBox
)
from PySide6.QtCore import Qt, QSize
from spotify_api import SpotifyAPI
from outlined_label import OutlinedLabel
from would_you_rather import ClickableTrackWidget
from ranking_display import HistoryDialog, RankingDialog
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
        
        self.current_challenger = None              # When the game starts, there is no current challenger(no winner yet)
        self.remaining_songs = self.selected_items.copy()
        self.match_history = []
        self.final_ranking = []
        self.isEndless = self.api is not None       # Easy Check for endless
        

        # Background - Main Window
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
        title_label = OutlinedLabel("Choose Your Favorite!")
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
        
        vs_label = OutlinedLabel("VS")
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

        # History Button is hidden until the game is done(NORMAL MODE)
        self.show_history_button = QPushButton("Show History")
        self.show_history_button.clicked.connect(self.show_match_history)
        self.show_history_button.clicked.connect(self.show_final_ranking)
        self.show_history_button.setStyleSheet(self.button_style())
        if not self.isEndless:
            self.show_history_button.hide()  

        control_layout.addWidget(self.new_round_button)
        control_layout.addWidget(self.back_button)
        control_layout.addWidget(self.show_history_button)
        main_layout.addLayout(control_layout)

        # Check if we have enough items before starting the game
        if len(self.selected_items) >= 2:
            self.start_new_round(first_round=True)
        else:
            # Show placeholder content or disable the game
            self.show_not_enough_items_message()
    
    
    # Show match history in a message box - will be a new window eventually
    def show_final_ranking(self):
        if not self.final_ranking:
            QMessageBox.information(self, "No Ranking", "No final ranking available yet!")
            return

        dlg = RankingDialog(self.final_ranking, self)
        dlg.exec()


    def show_match_history(self):
        if not self.match_history:
            QMessageBox.information(self, "No History", "No matches have been played yet!")
            return

        dlg = HistoryDialog(self.match_history, self)
        dlg.exec()
    
    # Reset Game
    def reset_tournament(self):
        """Reset the tournament to start over"""
        self.remaining_songs = self.selected_items.copy()
        self.match_history = []
        self.final_ranking = []
        self.current_challenger = None
        self.show_history_button.hide()
        self.new_round_button.setText("New Round")
        self.new_round_button.show()
    
    
    # Not currently implemented [TODO] 
    def show_not_enough_items_message(self):
        """Show a message when there aren't enough items to start the game"""
        # You can customize this to show a better message in the game area
        placeholder_label = OutlinedLabel("Not enough items selected to start the game!")
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
        
    # Default button style for the bottom part of the window(exit, new game, match history)
    def button_style(self):
        return """
            QPushButton {
                font-size: 12px;
                font-weight: bold;
                padding: 8px 16px;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                background-color: rgba(0, 0, 0, 0.7);
                color: white;
                min-width: 80px;
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
        if self.isEndless:
            # TODO: Endless mode logic
            pass
        else:
            # Tournament mode

            # Prevent starting a round only if we have fewer than 2 songs (but allow exactly 2)
            if first_round and len(self.remaining_songs) < 2:
               QMessageBox.warning(self, "Not Enough Items",
                                    "You need at least 2 items selected to play the game!")
               return

            # Tournament complete if only 1 song remains
            if len(self.remaining_songs) == 1:
                winner = self.remaining_songs[0]
                self.final_ranking.insert(0, winner)  # Winner goes to the front

                msg = QMessageBox(self)
                msg.setWindowTitle("Tournament Complete!")
                msg.setText(f"🏆 WINNER: {winner.track_name} by {winner.artist_name} 🏆\n\nClick 'Show History' to see the full results!")
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: rgba(43, 43, 43, 180);
                        color: white;
                        font-size: 14px;
                    }
                    QMessageBox QPushButton {
                        background-color: rgba(43, 43, 43, 180);
                        color: white;
                        border: 1px solid #666;
                        padding: 5px 15px;
                        border-radius: 3px;
                    }
                """)
                msg.exec()

                # Hide game elements and show history button
                self.left_widget.hide()
                self.right_widget.hide()
                self.new_round_button.hide()
                self.show_history_button.show()
                return

            # If this is the first round or there is no current challenger, pick two random songs
            if first_round or not self.current_challenger:
                self.current_pair = random.sample(self.remaining_songs, 2)
                self.current_challenger = self.current_pair[0]  # default challenger
            else:
                # Challenger stays, pick a new random opponent
                available = [item for item in self.remaining_songs if item != self.current_challenger]
                if not available:
                    return
                new_opponent = random.choice(available)
                self.current_pair = [self.current_challenger, new_opponent]

            self.left_widget.update_track(self.current_pair[0])
            self.right_widget.update_track(self.current_pair[1])

    def format_item_text(self, item):
        return f"{item.artist_name}\n\n{item.album_name}\n\n{item.track_name}"

    def on_choice_made(self, choice):
        chosen_item = self.current_pair[0] if choice == "left" else self.current_pair[1]
        eliminated_item = self.current_pair[1] if choice == "left" else self.current_pair[0]
        
        print(f"User chose: {chosen_item.track_name} by {chosen_item.artist_name}")
        
        if self.isEndless:
            # Endless mode - old logic
            self.current_challenger = chosen_item
            self.start_new_round()
        else:
            # Tournament mode - track matches and eliminate songs
            match_description = f"{chosen_item.track_name} VS {eliminated_item.track_name} - {chosen_item.track_name} WON"
            self.match_history.append((chosen_item, eliminated_item, match_description))
            
            # Remove eliminated song from remaining songs
            if eliminated_item in self.remaining_songs:
                self.remaining_songs.remove(eliminated_item)
                # Add to final ranking (losers go to the back in reverse order of elimination)
                self.final_ranking.append(eliminated_item)
            
            # Update challenger
            self.current_challenger = chosen_item
            
            # Show remaining count in console for debugging
            print(f"Remaining songs: {len(self.remaining_songs)}")
            for song in self.remaining_songs:
                print(f"  - {song.track_name}")
            
            self.start_new_round()
        
    def go_back_to_main(self):
        self.close()
        self.return_to_main_callback()