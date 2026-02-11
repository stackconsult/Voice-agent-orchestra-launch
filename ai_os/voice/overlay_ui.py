import sys
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont

class VoiceOverlay:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = OverlayWindow()
        
    def run(self):
        self.app.exec()
        
    def show_state(self, state, message=""):
        self.window.update_state(state, message)

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint | 
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Position: Top Right or Bottom Center
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen.width() - 320, 40, 300, 100) # Top right
        
        layout = QVBoxLayout()
        self.label = QLabel("Waiting...")
        self.label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.label.setStyleSheet("color: white; padding: 10px;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Styles
        self.styles = {
            "listening": "background-color: rgba(220, 53, 69, 0.8); border-radius: 10px;", # Red
            "processing": "background-color: rgba(23, 162, 184, 0.8); border-radius: 10px;", # Blue
            "success": "background-color: rgba(40, 167, 69, 0.8); border-radius: 10px;", # Green
            "error": "background-color: rgba(52, 58, 64, 0.8); border-radius: 10px;" # Dark
        }
        
        self.setStyleSheet(self.styles["error"])
        self.hide()

    def update_state(self, state, message=""):
        if state in self.styles:
            self.setStyleSheet(self.styles[state])
            
        text_map = {
            "listening": "🎙️ Listening...",
            "processing": "🧠 Thinking...",
            "generating": "⚙️ Building Skill...",
            "executing": "⚡ Executing...",
            "success": f"✅ {message}" if message else "✅ Done",
            "error": f"❌ {message}" if message else "❌ Error"
        }
        
        self.label.setText(text_map.get(state, message))
        self.show()
        
        if state in ["success", "error"]:
            QTimer.singleShot(3000, self.hide)
