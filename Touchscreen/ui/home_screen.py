from PyQt5.QtWidgets import QTextEdit, QSizePolicy, QWidget, QVBoxLayout, QLabel, QGridLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

FONT = "Calibri"

class HomeScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        grid = QGridLayout()
        self.setLayout(grid)

        grid.setSpacing(15)
        grid.setContentsMargins(15, 15, 15, 15)

        #set screen size to size of touchscreen
        self.setMinimumSize(800, 480)
              
        #title - span across top
        title = QLabel("Home Screen")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont(FONT, 16)) 
        title.setFixedHeight(40)
        grid.addWidget(title, 0, 0, 1, 2)  # row, col, rowspan, colspan

        #buttons
        idle_button = QPushButton("Go to Idle Screen")
        scan_button = QPushButton("Go to Scan Screen")
        solve_button = QPushButton("Go to Solve Screen")

        #status area
        cube_status = QLabel("\nCube Status\n\nMounted: FALSE\nLast Scan: 04/20/2026 15:32:13 PST\nLast Scramble: 04/20/2026 15:32:24 PST\nSolved: FALSE")
        cube_status.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        cube_status.setFont(QFont(FONT, 24))

        #warning area
        warning_label = QLabel("No warnings")
        warning_label.setAlignment(Qt.AlignCenter)      
        warning_label.setFont(QFont(FONT, 8))
        warning_label.setStyleSheet("color: green;")
            #how to update later: warning_label.setText("Warning: Camera disconnected")

        # Make buttons expand
        for btn in [cube_status, idle_button, scan_button, solve_button]:
            #btn.setMinimumSize(150, 100)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            btn.setFont(QFont(FONT, 9))

        
        # Place in grid (2x2)
        grid.addWidget(cube_status, 1, 0)
        grid.addWidget(idle_button, 1, 1)
        grid.addWidget(scan_button, 2, 0)
        grid.addWidget(solve_button, 2, 1)
        grid.addWidget(warning_label, 3, 0, 1, 2)  # span across both columns

        # Make rows/columns stretch (fill screen)
        grid.setRowStretch(0, 0)
        grid.setRowStretch(1, 1)
        grid.setRowStretch(2, 1)
        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)
        grid.setRowStretch(3, 0)  # don't let it grow

        #travel between screens
        idle_button.clicked.connect(self.main_window.show_idle)
        scan_button.clicked.connect(self.main_window.show_scan)
        solve_button.clicked.connect(self.main_window.show_solve)

