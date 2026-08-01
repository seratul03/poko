import sys
import os
import config
from PySide6.QtWidgets import QApplication
from src.core.app import NekoApp
from src.utils.logger import setup_logger, get_logger

def main():

    setup_logger()
    logger = get_logger(__name__)
    logger.info(f"Starting {config.APP_NAME}...")
    
    app = QApplication(sys.argv)
    
    try:
        
        neko_app = NekoApp(app)
        neko_app.run()
        
        sys.exit(app.exec())
    except Exception as e:
        logger.exception("A fatal error occurred")
        sys.exit(1)

if __name__ == "__main__":
    main()
