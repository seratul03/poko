import os
from pathlib import Path
from PySide6.QtGui import QPixmap
import config
from src.utils.logger import get_logger

logger = get_logger(__name__)

def load_animations() -> dict[str, list[QPixmap]]:
    """
    Loads all animations from the assets/animations directory.
    Returns a dictionary of {animation_name: [QPixmap, QPixmap, ...]}.
    """
    animations = {}
    
    if not config.ANIMATIONS_DIR.exists():
        logger.warning(f"Animations directory not found: {config.ANIMATIONS_DIR}")
        return animations
        
    for anim_dir in config.ANIMATIONS_DIR.iterdir():
        if anim_dir.is_dir():
            anim_name = anim_dir.name
            frames = []
            
            # Load frames (assume they are named like frame0.png, frame1.png, etc.)
            # Sort them properly
            file_list = list(anim_dir.glob("*.png"))
            # Custom sort to handle frame0, frame1, ..., frame10 correctly
            file_list.sort(key=lambda x: x.stem)
            
            for file_path in file_list:
                pixmap = QPixmap(str(file_path))
                if pixmap.isNull():
                    logger.error(f"Failed to load image: {file_path}")
                else:
                    # Optional: scale the pixmap if needed. For pixel art, FastTransformation or no scaling might be better.
                    # pixmap = pixmap.scaled(config.PET_WIDTH, config.PET_HEIGHT, Qt.AspectRatioMode.KeepAspectRatio)
                    frames.append(pixmap)
                    
            if frames:
                animations[anim_name] = frames
                logger.debug(f"Loaded animation '{anim_name}' with {len(frames)} frames.")
            else:
                logger.warning(f"No frames found for animation '{anim_name}' in {anim_dir}")
                
    return animations
