from PySide6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget, QMessageBox, QStackedWidget, QSizePolicy  # Added QStackedWidget
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

        self.api = spotify_api
        self.selected_items = selected_items or []
        self.return_to_main_callback = return_to_main_callback
        
        self.current_challenger = None
        self.remaining_songs = self.selected_items.copy()
        self.match_history = []
        self.final_ranking = []
        self.isEndless = self.api is not None

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
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Title with improved styling
        title_label = OutlinedLabel("Choose Your Favorite!")
        title_label.setAlignment(Qt.AlignHCenter)
        title_label.setFixedHeight(80)
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
        main_layout.addWidget(title_label, 0, Qt.AlignTop)
    
        
        # Create stacked widget to switch between game views
        self.game_stack = QStackedWidget()
        main_layout.addWidget(self.game_stack, stretch=1)  # Takes most space
        
        # Page 1: Normal game view (two tracks)
        self.normal_page = QWidget()
        normal_layout = QHBoxLayout(self.normal_page)
        normal_layout.setContentsMargins(0, 0, 0, 0)
        normal_layout.setSpacing(0)
        
        self.left_widget = ClickableTrackWidget()
        self.right_widget = ClickableTrackWidget()
        
        normal_layout.addWidget(self.left_widget, stretch=1)
        normal_layout.addWidget(self.right_widget, stretch=1)
        
        # Page 2: Winner display view
        self.winner_page = QWidget()
        self.winner_layout = QHBoxLayout(self.winner_page)
        self.winner_layout.setContentsMargins(20, 20, 20, 20)
        self.winner_layout.setSpacing(10)

        # Winner widget setup
        self.winner_widget = ClickableTrackWidget()
        self.winner_widget.set_hover_effect(False)
        self.winner_widget.set_clickable(False)
        self.winner_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.winner_widget.setMinimumSize(300, 300)
        

        # Buttons
        self.left_button = QPushButton("◀ Check History")
        self.left_button.setStyleSheet(self.button_style())
        self.left_button.setMaximumWidth(150)
        self.left_button.clicked.connect(self.show_match_history)

        self.right_button = QPushButton("Check Full Ranking ▶")
        self.right_button.setStyleSheet(self.button_style())
        self.right_button.setMaximumWidth(150)
        self.right_button.clicked.connect(self.show_final_ranking)

        # Add them once to layout
        self.winner_layout.addWidget(self.left_button, stretch=1)
        self.winner_layout.addWidget(self.winner_widget, stretch=1)
        self.winner_layout.addWidget(self.right_button, stretch=1)

        # Add both pages to stack (start with normal view)
        self.game_stack.addWidget(self.normal_page)
        self.game_stack.addWidget(self.winner_page)
        
        
        # Connect click handlers
        self.left_widget.clicked.connect(lambda: self.on_choice_made("left"))
        self.right_widget.clicked.connect(lambda: self.on_choice_made("right"))
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(20, 10, 20, 10)
        
        self.new_round_button = QPushButton("New Round")
        self.new_round_button.clicked.connect(self.start_new_round)
        self.new_round_button.setStyleSheet(self.button_style())

        self.back_button = QPushButton("Back to Main")
        self.back_button.clicked.connect(self.go_back_to_main)
        self.back_button.setStyleSheet(self.button_style())

        self.show_history_button = QPushButton("Show History")
        self.show_history_button.clicked.connect(self.show_match_history)
        self.show_history_button.setStyleSheet(self.button_style())
        if not self.isEndless:
            self.show_history_button.hide()  

        control_layout.addWidget(self.new_round_button)
        control_layout.addWidget(self.back_button)
        control_layout.addWidget(self.show_history_button)
        main_layout.addLayout(control_layout)

        # Check if we have enough items
        if len(self.selected_items) >= 2:
            self.start_new_round(first_round=True)
        else:
            self.show_not_enough_items_message()
    
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
    
    def reset_tournament(self):
        """Reset the tournament to start over"""
        self.remaining_songs = self.selected_items.copy()
        self.match_history = []
        self.final_ranking = []
        self.current_challenger = None
        self.show_history_button.hide()
        self.new_round_button.setText("New Round")
        self.new_round_button.show()
        
        #######################################################################
        # CHANGED: Switch back to normal view when resetting tournament        #
        #######################################################################
        self.game_stack.setCurrentWidget(self.normal_page)
        #######################################################################
    
    def show_not_enough_items_message(self):
        """Show a message when there aren't enough items to start the game"""
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
            if len(self.remaining_songs) < 2:
                self.remaining_songs.append(self.api.endless_mode())
            
        else:
            if first_round and len(self.remaining_songs) < 2:
               QMessageBox.warning(self, "Not Enough Items",
                                    "You need at least 2 items selected to play the game!")
               return

        # Tournament complete if only 1 song remains
        if len(self.remaining_songs) == 1:
            winner = self.remaining_songs[0]
            self.final_ranking.insert(0, winner)

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

            # Switch to winner widget - Match History, Ranking, Winner Song Cover
            self.winner_widget.update_track(winner)
            self.game_stack.setCurrentWidget(self.winner_page)
            self.new_round_button.hide()
            self.show_history_button.show()

        else:
            # Normal round logic
            if first_round or not self.current_challenger:
                self.current_pair = random.sample(self.remaining_songs, 2)
                self.current_challenger = self.current_pair[0]
            else:
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
        # Format match for the match history
        match_description = f"{chosen_item.track_name} VS {eliminated_item.track_name} - {chosen_item.track_name} WON"
        self.match_history.append((chosen_item, eliminated_item, match_description))

        print(f"User chose: {chosen_item.track_name} by {chosen_item.artist_name}")
        if self.isEndless:
            if eliminated_item in self.remaining_songs:
                self.remaining_songs.remove(eliminated_item)
                print(f"Removed {eliminated_item.track_name} from pool")
        
            new_song = self.api.endless_mode()
            self.remaining_songs.append(new_song)
            print(f"Added {new_song.track_name} to pool")
        
            self.current_challenger = chosen_item
        
            self.start_new_round()
        else:
            match_description = f"{chosen_item.track_name} VS {eliminated_item.track_name} - {chosen_item.track_name} WON"
            self.match_history.append((chosen_item, eliminated_item, match_description))
            
            if eliminated_item in self.remaining_songs:
                self.remaining_songs.remove(eliminated_item)

                # FIXED: Handle final placement correctly
                if len(self.remaining_songs) == 1:
                    # This was the final match - eliminated item gets 2nd place
                    self.final_ranking.insert(0, eliminated_item)
                else:
                    # Regular elimination - insert at beginning (lower ranks go to front)
                    self.final_ranking.insert(0, eliminated_item)
            
            self.current_challenger = chosen_item
            
            print(f"Remaining songs: {len(self.remaining_songs)}")
            for song in self.remaining_songs:
                print(f"  - {song.track_name}")
            
            self.start_new_round()
        
    def go_back_to_main(self):
        if self.api:
            self.api.shutdown()
        self.close()
        self.return_to_main_callback()