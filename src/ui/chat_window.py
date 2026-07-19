from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QTextEdit, QLineEdit, QPushButton)
from PySide6.QtCore import Qt

class ChatWindow(QDialog):
    def __init__(self, app_context, parent=None):
        super().__init__(parent)
        self.app_context = app_context
        
        self.setWindowTitle("Chat with Neko")
        self.resize(400, 300)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # History
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        layout.addWidget(self.history_display)
        
        # Load history
        if self.app_context.memory:
            history = self.app_context.memory.get_chat_history()
            for msg in history:
                self.history_display.append(f"<b>You:</b> {msg['user']}")
                self.history_display.append(f"<b>Neko:</b> {msg['ai']}<br>")
                
        # Input area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
    def send_message(self):
        text = self.input_field.text().strip()
        if not text:
            return
            
        self.input_field.clear()
        self.history_display.append(f"<b>You:</b> {text}")
        
        # Call AI
        if self.app_context.ai:
            reply = self.app_context.ai.send_message(text)
            self.history_display.append(f"<b>Neko:</b> {reply}<br>")
            
            # Show speech bubble too
            if self.app_context.speech_bubble:
                self.app_context.speech_bubble.show_message(reply)
                
            # Update mood based on conversation
            if self.app_context.mood:
                self.app_context.mood.add_mood(2) # Small boost for talking
        else:
            self.history_display.append(f"<b>Neko:</b> ... (AI disabled)<br>")
