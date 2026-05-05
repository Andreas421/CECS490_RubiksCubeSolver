from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt


class ScanScreen(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.setMinimumSize(800, 480)
        self.resize(800, 480)

        layout = QVBoxLayout()

        label = QLabel("Scan Screen")
        label.setAlignment(Qt.AlignCenter)

        back_button = QPushButton("Back to Home")

        back_button.clicked.connect(self.main_window.show_home)

        layout.addWidget(label)
        layout.addWidget(back_button)

        self.setLayout(layout)