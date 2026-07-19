import json
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                               QLabel, QSlider, QCheckBox, QPushButton, QMessageBox)
from PySide6.QtCore import Qt
import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

class SettingsWindow(QDialog):
    def __init__(self, app_context, parent=None):
        super().__init__(parent)
        self.app_context = app_context
        self.settings = self._load_settings()
        
        self.setWindowTitle(f"{config.APP_NAME} Settings")
        self.setFixedSize(300, 250)
        
        self.init_ui()
        
    def _load_settings(self):
        settings = config.DEFAULT_SETTINGS.copy()
        if config.SETTINGS_FILE.exists():
            try:
                with open(config.SETTINGS_FILE, 'r') as f:
                    settings.update(json.load(f))
            except Exception as e:
                logger.error(f"Failed to load settings: {e}")
        return settings
        
    def _save_settings(self):
        try:
            with open(config.SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Volume
        vol_layout = QHBoxLayout()
        vol_layout.addWidget(QLabel("Volume:"))
        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(self.settings.get("volume", 50))
        vol_layout.addWidget(self.vol_slider)
        layout.addLayout(vol_layout)
        
        # Enable AI
        self.ai_checkbox = QCheckBox("Enable AI Chat (Requires API Key)")
        self.ai_checkbox.setChecked(self.settings.get("enable_ai", False))
        layout.addWidget(self.ai_checkbox)
        
        # Always on top
        self.top_checkbox = QCheckBox("Always on Top")
        self.top_checkbox.setChecked(self.settings.get("always_on_top", True))
        layout.addWidget(self.top_checkbox)
        
        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_and_close)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
    def save_and_close(self):
        self.settings["volume"] = self.vol_slider.value()
        self.settings["enable_ai"] = self.ai_checkbox.isChecked()
        self.settings["always_on_top"] = self.top_checkbox.isChecked()
        
        self._save_settings()
        
        # Apply volume if sound system exists
        if self.app_context and hasattr(self.app_context, 'sound'):
            if self.app_context.sound:
                self.app_context.sound.set_volume(self.settings["volume"] / 100.0)
                
        # Apply window flags
        if self.app_context and hasattr(self.app_context, 'pet_window'):
            # Re-apply window flags without breaking transparency
            window = self.app_context.pet_window
            flags = Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool
            if self.settings["always_on_top"]:
                flags |= Qt.WindowType.WindowStaysOnTopHint
            
            window.setWindowFlags(flags)
            window.show() # Need to call show again after changing flags
            
        self.accept()
