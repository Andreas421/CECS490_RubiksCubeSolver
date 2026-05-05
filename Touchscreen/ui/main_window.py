from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from ui.home_screen import HomeScreen
from ui.idle_screen import IdleScreen
from ui.scan_screen import ScanScreen
from ui.solve_screen import SolveScreen


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screen Navigation Demo")

        self.stack = QStackedWidget()

        self.home_screen = HomeScreen(self)
        self.idle_screen = IdleScreen(self)
        self.scan_screen = ScanScreen(self)
        self.solve_screen = SolveScreen(self)

        self.stack.addWidget(self.home_screen)
        self.stack.addWidget(self.idle_screen)
        self.stack.addWidget(self.scan_screen)
        self.stack.addWidget(self.solve_screen)

        self.setCentralWidget(self.stack)

        self.show_home()

    def show_home(self):
        self.stack.setCurrentWidget(self.home_screen)

    def show_idle(self):
        self.stack.setCurrentWidget(self.idle_screen)

    def show_scan(self):
        self.stack.setCurrentWidget(self.scan_screen)

    def show_solve(self):
        self.stack.setCurrentWidget(self.solve_screen)