import os
import sys

# Add the current directory to the path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from .src.nodes import AspectRatioResizer, AutoMegapixelReducer # type: ignore
except ImportError:
    from src.nodes import AspectRatioResizer, AutoMegapixelReducer # type: ignore

NODE_CLASS_MAPPINGS = {
    "AspectRatioResizer": AspectRatioResizer,
    "AutoMegapixelReducer": AutoMegapixelReducer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AspectRatioResizer": "Aspect Ratio Resizer (nvmaxx)",
    "AutoMegapixelReducer": "Auto Megapixel Reducer (nvmaxx)",
}

# FIX: Removed the leading "./" which breaks registry path parsers
WEB_DIRECTORY = "web/js"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']
