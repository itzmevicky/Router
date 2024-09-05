from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtCore import Qt

class Column(QWidget):
    def __init__(self, text, width_factor, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: #D1E9F6;" 
            "border: 1px solid #B0B0B0;"  
        )
        self.setMinimumHeight(0)
        layout = QVBoxLayout()
        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter)  
        layout.addWidget(label)
        layout.setContentsMargins(0, 5, 0, 0)  
        layout.setSpacing(0)  
        self.setLayout(layout)

        # Set the size policy to allow resizing
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.width_factor = width_factor

class Section(QWidget):
    def __init__(self, column_details, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: #D1E9F6;"  # Background color for sections
            "border: 1px solid #B0B0B0;"  # Border color and width
        )
        self.setMinimumHeight(0)
        section_layout = QHBoxLayout()
        section_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        section_layout.setSpacing(0)  # No spacing between widgets

        for text, width in column_details:
            column = Column(text, width)
            section_layout.addWidget(column, width)
        
        self.setLayout(section_layout)

class TopRowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: #D1E9F6;"  # Background color for top row
            "border: 1px solid #B0B0B0;"  # Border color and width
        )
        self.setMinimumHeight(0)

        top_row_layout = QVBoxLayout()

        column_details = [
            ("Router", 6),
            ("TFTP ", 1),
            ("GSM", 3),
        ]

        section1 = Section(column_details)
        section2 = Section(column_details)
        section3 = Section(column_details)

        top_row_layout.addWidget(section1, 1)
        top_row_layout.addWidget(section2, 1)
        top_row_layout.addWidget(section3, 1)

        top_row_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        top_row_layout.setSpacing(0)  # No spacing between widgets

        self.setLayout(top_row_layout)

class BottomRowWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "background-color: #D1E9F6;"  # Background color for bottom row
            "border: 1px solid #B0B0B0;"  # Border color and width
        )
        self.setMinimumHeight(0)

        layout = QVBoxLayout()
        label = QLabel("20% Height Row")
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)  # No margins
        layout.setSpacing(0)  # No spacing between widgets
        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Router Installation")
        self.setStyleSheet("background-color: #D1E9F6;")  # Universal background color

        main_layout = QVBoxLayout()

        top_row_widget = TopRowWidget()
        bottom_row_widget = BottomRowWidget()

        main_layout.addWidget(top_row_widget, 9)  # 80% height
        main_layout.addWidget(bottom_row_widget, 1)  # 20% height

        main_layout.setContentsMargins(0, 0, 0, 0)  # No margins
        main_layout.setSpacing(0)  # No spacing between widgets

        self.setLayout(main_layout)
        self.resize(800, 600)  # Set an initial size

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
