"""
stegochess - Chess Endgame Steganography Package
Combines YOLO detection with STRIPS planning
"""

__version__ = "0.1.0"

# Import main modules for easy access
from . import board
from . import model
from . import solver
from . import ChessPredictor

__all__ = ['board', 'model', 'solver', 'ChessPredictor']
