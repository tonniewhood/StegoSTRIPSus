"""
detection.py - YOLO-based chess piece detection
"""

import os
from pathlib import Path
from typing import Dict, Tuple

import chess
from PIL import Image
from ultralytics import YOLO

from stegochess.ChessPredictor import ChessPiecePredictor

def evalute(args):
    # Quick checks for file existence
    if not args.board and not args.fen_string:
        print("Either --board (-b) or --fen-string (-f) must be provided.")
        return
    if not os.path.exists(args.model_path):
        print(f"Model file '{args.model_path}' does not exist.")
        return
    if not os.path.exists(args.board) and not args.fen_string:
        print(f"Board image '{args.board}' does not exist.")
        return

    predictor = ChessPiecePredictor(model_path=args.model_path, device=args.device, confidence_threshold=args.confidence_threshold)
    
    if args.board:
        # Load board image
        try:
            board_image = Image.open(args.board)
            if board_image.mode == "GIF":
                board_image = board_image.convert("RGB").convert("RGBA")
            elif board_image.mode != "RGBA":
                board_image = board_image.convert("RGBA")
        except Exception as e:
            print(f"Failed to open board image '{args.board}': {e}")
            return
    else:
        background_image = Image.open(BOARD_FILE.format(args.board_style)).convert("RGBA")
        piece_images = {
            chess.WHITE: {},
            chess.BLACK: {}
        }
        for color in [chess.WHITE, chess.BLACK]:
            for piece_type in chess.PIECE_TYPES:
                piece_file = SPRITE_DIR + PIECE_IMAGES[color][piece_type].format(args.piece_style)
                piece_img = Image.open(piece_file).convert("RGBA")
                piece_images[color][piece_type] = piece_img

        board_image = generate_board_image(background_image, piece_images, args.fen_string, use_invalid_fen=True)
        if board_image is None:
            print("Failed to generate board image from FEN string.")
            return
        
        if args.fen_board_output:
            board_image.save(args.fen_board_output)
            print(f"Generated board image saved to {args.fen_board_output}")

    if args.resize_board:
        board_image = board_image.resize((1200, 1200), Image.ANTIALIAS)
        
    row_labels = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
    predicted_fen, avg_confidence, square_confidences = predictor.predict_board(board_image, return_confidence=True)
    print(f"Predicted FEN: {predicted_fen}")
    print(f"Average Confidence: {avg_confidence:.4f}")
    print("Square Confidences:")
    for rank in range(8, 0, -1):
        row_confidences = []
        for file in range(1, 9):
            confidence = square_confidences.get(f"{row_labels[rank - 1]}{file}", 0.0)
            row_confidences.append(f"{confidence:.2f}")
        print(row_labels[rank - 1], " ", " ".join(row_confidences))

    print(f"\n {' '.join([f'{x:4}' for x in range(1,9)])}")
    print("\nPredicted Board State:")
    board = chess.Board(predicted_fen)
    print(board)

    if args.fen_string:
        expected_board = chess.Board(args.fen_string)
        is_correct = board.board_fen() == expected_board.board_fen()
        print(f"Prediction Correct: {is_correct}")

def detect_from_image(image: Image.Image, model_path: Path, device: int = 0, confidence_threshold: float = 0.5) -> Tuple[str, str | float, str | Dict[str, float]]:
    """
    Run YOLO detection on a chess board image

    Args:
        image (Image.Image): PIL Image of the chess board
        model_path (Path): Path to the YOLO model
        device (int): Device index for YOLO model (e.g., 0 for GPU, -1 for CPU)
        confidence_threshold (float): Minimum confidence for predictions (0-1)

    Returns:
        Tuple[str, str | float, str | Dict[str, float]]: the predicted FEN string, average confidence, and per-square confidences
    """
    
    print("[DETECTION] Processing image for detection")
    predictor = ChessPiecePredictor(model_path=model_path, device=device, confidence_threshold=confidence_threshold)
    return predictor.predict_board(image, return_confidence=True)


def detection_to_fen(detection_results):
    """
    Convert YOLO detection results to FEN string

    Args:
        detection_results: Dict of detected pieces and positions

    Returns:
        str: FEN string representation
    """
    print("[DETECTION] Converting detection to FEN")
    # TODO: Implement conversion
    return ""
