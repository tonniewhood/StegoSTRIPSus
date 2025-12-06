
import argparse
import os

from pathlib import Path
from typing import Tuple, Union, List, Dict
from PIL import Image
from ultralytics import YOLO


class ChessPiecePredictor:
    """
    Predicts chess piece types from square images.
    Works with in-memory images (numpy arrays, PIL Images).
    """
    
    def __init__(self, model_path: Union[str, Path], device: int | None = None, confidence_threshold: float = 0.5):
        """
        Initialize the predictor with a trained model.
        
        Args:
            model_path: Path to the trained model weights (.pt file)
            confidence_threshold: Minimum confidence for predictions (0-1)
        """
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        self.model = YOLO(str(model_path))
        self.device = device
        self.confidence_threshold = confidence_threshold
        
        # Get class names from model
        self.class_names = self.model.names  # Dict: {0: 'bb', 1: 'bk', ...}
        print(f"[PREDICTOR] Loaded model: {model_path}")
        print(f"[PREDICTOR] Classes: {list(self.class_names.values())}\n")
    
    def predict_square(self, image: Image.Image, 
                       return_confidence: bool = False) -> str | Tuple[str, float]:
        """
        Predict the piece on a single chess square.
        
        Args:
            image (Image.Image): Square image as a PIL Image
            return_confidence: If True, return confidence score

        Returns:
            If return_confidence=False: String with predicted class name (e.g., 'wq', 'empty')
            If return_confidence=True: Tuple with (class_name, confidence)
        """
        if self.device is not None:
            self.model.to(self.device)

        # Run prediction (verbose=False to suppress output)
        results = self.model(image, verbose=False)[0]
        
        # Get top prediction
        probs = results.probs  # Classification probabilities
        top_class_id = probs.top1  # Index of top class
        top_confidence = probs.top1conf.item()  # Confidence value
        top_class_name = self.class_names[top_class_id]
        
        if return_confidence:
            return top_class_name, top_confidence
        else:
            # Return just the predicted class name
            return top_class_name

    def predict_squares(self, squares: List[Image.Image], 
                       return_confidence: bool = False) -> List[Union[str, Tuple[str, float]]]:
        """
        Predict pieces on multiple chess squares (batch prediction).
        
        Args:
            images: The board image as a PIL Image
            return_confidence: If True, return the overall confidence score (average over squares)
            
        Returns:
            If return_confidence=False: List of predicted class names
            If return_confidence=True: List of tuples (class_name, confidence) for each square
        """
        results = self.model(squares, verbose=False)

        predictions = []
        for result in results:
            top_class_id = result.probs.top1
            top_confidence = result.probs.top1conf.item()
            top_class_name = self.class_names[top_class_id]
            predictions.append((top_class_name, top_confidence))

        if return_confidence:
            return predictions
        else:
            return [pred[0] for pred in predictions]
    
    def predict_board(self, board: Image.Image,
                     return_confidence: bool = False) -> str | Tuple[str, float, Dict[str, float]]:
        """
        Predict pieces on an entire board (8x8 grid of squares).
        
        Args:
            square_images: 8x8 nested list of square images (row by row, a8 to h1)
            return_confidence: If True, return confidence scores
            
        Returns:
            If return_confidence=False: FEN string of predicted board state
            If return_confidence=True: Tuple with (FEN string, average confidence, per-square confidences)
        """
        # Crop the board image into individual square images
        squares = []
        for row in range(8):
            for col in range(8):
                x = col * (board.width // 8)
                y = row * (board.height // 8)
                square = board.crop((x, y, x + (board.width // 8), y + (board.height // 8)))
                squares.append(square)

        predictions = self.predict_squares(squares, return_confidence=return_confidence)
        avg_confidence = sum(pred[1] for pred in predictions) / len(predictions) if return_confidence else 1.0

        # Construct FEN string
        fen_rows = []
        for row in range(8):
            fen_row = ""
            empty_count = 0
            for col in range(8):
                class_name, _ = predictions[row * 8 + col]
                if class_name == 'empty':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += class_name[1].upper() if class_name[0] == 'w' else class_name[1].lower()
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)

        fen_string = "/".join(fen_rows) + " w - - 0 1"  # Simplified FEN suffix
        if return_confidence:
            cols = ["a", "b", "c", "d", "e", "f", "g", "h"]
            per_square_confidences = {f"{cols[i % 8]}{j}": conf for i, (_, conf) in enumerate(predictions) for j in range(1, 9)}
            return fen_string, avg_confidence, per_square_confidences
        else:
            return fen_string
        