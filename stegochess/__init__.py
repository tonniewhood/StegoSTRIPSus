"""
stegochess - Chess Endgame Steganography Package
Combines YOLO detection with STRIPS planning
"""

__version__ = "0.1.0"

# Import main modules for easy access
from . import detection
from . import solver
from . import board
from . import ChessPredictor

__all__ = ['detection', 'solver', 'board', 'ChessPredictor']
