from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QHBoxLayout, QWidget, QSizePolicy, QAbstractItemView
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class RankingDialog(QDialog):
    def __init__(self, final_ranking, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Final Ranking")
        self.resize(600, 700)

        layout = QVBoxLayout(self)

        title_label = QLabel("🏆 FINAL RANKING 🏆")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["#", "Cover", "Track Name", "Artist", "Album (Year)"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: white;
                gridline-color: #444;
                font-size: 14px;
        }
            QHeaderView::section {
                background-color: #444;
                color: white;
                font-weight: bold;
        }
            QTableWidget::item:selected {
                background-color: #555 !important;
                color: white;
        }
        """)

        self.table.setRowCount(len(final_ranking))
        for i, song in enumerate(final_ranking):
            # Rank number
            rank_item = QTableWidgetItem(str(i + 1))
            rank_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, rank_item)

            # Album cover thumbnail
            cover_item = QTableWidgetItem()
            if song.image_pixmap:
                # Scale pixmap to thumbnail size
                thumbnail = song.image_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                cover_item.setData(Qt.DecorationRole, thumbnail)
            self.table.setItem(i, 1, cover_item)
            self.table.setRowHeight(i, 80)

            # Track Name
            track_item = QTableWidgetItem(song.track_name)
            self.table.setItem(i, 2, track_item)

            # Artist Name
            artist_item = QTableWidgetItem(song.artist_name)
            self.table.setItem(i, 3, artist_item)

            # Album and year
            album_item = QTableWidgetItem(f"{song.album_name} ({song.release_year})")
            self.table.setItem(i, 4, album_item)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)


        layout.addWidget(self.table)
        
        # Button area
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)

        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)


class HistoryDialog(QDialog):
    def __init__(self, match_history, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Match History")
        self.resize(700, 700)  # Keep original size

        layout = QVBoxLayout(self)

        # Title with emoji and styling matching RankingDialog
        title_label = QLabel("📋 MATCH HISTORY 📋")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; padding: 10px;")
        layout.addWidget(title_label)

        # Table with consistent styling from RankingDialog
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["#", "Winner", "Loser", "Match Description"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setAlternatingRowColors(False)  # Changed to False to match RankingDialog
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #2b2b2b;
                color: white;
                gridline-color: #444;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #444;
                color: white;
                font-weight: bold;
            }
            QTableWidget::item:selected {
                background-color: #555 !important;
                color: white;
            }
        """)  

        self.table.setRowCount(len(match_history))
        for i, (winner, loser, description) in enumerate(match_history):
            # Index column
            idx_item = QTableWidgetItem(str(i + 1))
            idx_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, idx_item)

            # Winner column
            winner_item = QTableWidgetItem(winner.track_name)
            self.table.setItem(i, 1, winner_item)

            # Loser column
            loser_item = QTableWidgetItem(loser.track_name)
            self.table.setItem(i, 2, loser_item)

            # Description column
            desc_item = QTableWidgetItem(description)
            self.table.setItem(i, 3, desc_item)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)  

        btn_close = QPushButton("Close")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)

        layout.addLayout(btn_layout)
        

