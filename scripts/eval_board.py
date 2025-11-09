
import argparse
import os

import chess
from PIL import Image
from definitions.ChessPredictor import ChessPiecePredictor
from generate_boards import BOARD_FILE, PIECE_IMAGES, SPRITE_DIR, generate_board_image


def main(args: argparse.Namespace) -> None:
    """Evaluate a YOLO model on a chessboard dataset."""

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
        board_image = Image.open(args.board).convert("RGB")
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
        
    row_labels = ['h', 'g', 'f', 'e', 'd', 'c', 'b', 'a']
    predicted_fen, avg_confidence, square_confidences = predictor.predict_board(board_image, return_confidence=True)
    print(f"Predicted FEN: {predicted_fen}")
    print(f"Average Confidence: {avg_confidence:.4f}")
    print("Square Confidences:")
    for rank in range(8, 0, -1):
        row_confidences = []
        for file in range(1, 9):
            square = chess.square(file - 1, rank - 1)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate a YOLO model on a chessboard dataset.")
    parser.add_argument("--model-path", type=str, required=True, help="Path to the YOLO model file.")
    parser.add_argument("--board", "-b", type=str, default="", help="The path to the chess board set to evaluate the state of")
    parser.add_argument("--fen-string", "-f", type=str, default="", help="The FEN string representing the expected board state")
    parser.add_argument("--piece-style", type=str, default="neo", help="The style of chess pieces used in the board image. (Default: neo)")
    parser.add_argument("--board-style", type=str, default="green", help="The style of chess board used in the board image. (Default: green)")
    parser.add_argument("--confidence-threshold", type=float, default=0.5, help="Confidence threshold for predictions. (Default: 0.5)")
    parser.add_argument("--device", type=int, default=0, help="Device ID for evaluation. (Default: 0)")

    args = parser.parse_args()
    main(args)

