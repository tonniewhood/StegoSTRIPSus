
import argparse
import os
import random
import sys

from typing import Any, Dict, List

import cairosvg
import chess
import yaml

from PIL import Image
from io import BytesIO


# TB_PATH = "/home/tonniewhood/School/Fall_2025/CS_5600/Final_Project/tablebases/"
ASSET_PATH = "/home/tonniewhood/School/Fall_2025/CS_5600/Final_Project/assets/"
DATA_DIR = "/home/tonniewhood/School/Fall_2025/CS_5600/Final_Project/boardData"
BOARD_FILE = ASSET_PATH + "Chessboard.png"
SPRITE_DIR = ASSET_PATH + "sprites/"
PIECE_IMAGES = {
    chess.WHITE: {
        chess.PAWN: "white/pawn.svg",
        chess.KNIGHT: "white/knight.svg",
        chess.BISHOP: "white/bishop.svg",
        chess.ROOK: "white/rook.svg",
        chess.QUEEN: "white/queen.svg",
        chess.KING: "white/king.svg",
    },
    chess.BLACK: {
        chess.PAWN: "black/pawn.svg",
        chess.KNIGHT: "black/knight.svg",
        chess.BISHOP: "black/bishop.svg",
        chess.ROOK: "black/rook.svg",
        chess.QUEEN: "black/queen.svg",
        chess.KING: "black/king.svg",
    }
}

BOARD_WIDTH = 1152
BOARD_HEIGHT = 1152
SQUARE_SIZE = BOARD_WIDTH // 8
PIECE_WIDTH = int(SQUARE_SIZE * 0.85)
PIECE_HEIGHT = int(SQUARE_SIZE * 0.85)

def valid_board(board: chess.Board) -> bool:   
    """
    Check if the given chess board is invalid based on its status.

    Args:
        board (chess.Board): The chess board to check.

    Returns:
        bool: True if the board is invalid, False otherwise.
    """
    # Ignore all check-related status flags for endgame position generation
    CHECK_FLAGS = (
        chess.STATUS_BAD_CASTLING_RIGHTS |
        chess.STATUS_INVALID_EP_SQUARE |
        chess.STATUS_OPPOSITE_CHECK |
        chess.STATUS_TOO_MANY_CHECKERS |
        chess.STATUS_IMPOSSIBLE_CHECK
    )
    
    status = board.status() & ~CHECK_FLAGS
    return status == chess.STATUS_VALID


def generate_board_image(board_image: Image.Image, piece_images: Dict[chess.Color, Dict[chess.PieceType, Image.Image]], fen: str, output_path: str, use_invalid_fen: bool = False) -> None:
    """
    Generate a chess board image from a FEN string and save it to the specified output path.

    Args:
        board_image (Image.Image): The base image of the chess board.
        piece_images (List[Image.Image]): List of piece images indexed by color and piece type.
        fen (str): The FEN string representing the chess position.
        output_path (str): The path to save the generated image.
        use_invalid_fen (bool): If True, use an invalid FEN for testing purposes.
    """

    try:
        board = chess.Board(fen)
        if not valid_board(board):
            if not use_invalid_fen:
                return 1
            print("WARNING: Input FEN string is invalid. Proceeding due to request.")
    except ValueError:
        if not use_invalid_fen:
            return 1
        print("WARNING: Input FEN string is invalid. Proceeding due to request.")

    # Create a new image for the board
    board_state_img = board_image.copy()

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_img = piece_images[piece.color][piece.piece_type]
            row = 7 - (square // 8)
            col = square % 8
            x = col * SQUARE_SIZE + (SQUARE_SIZE - PIECE_WIDTH) // 2
            y = row * SQUARE_SIZE + (SQUARE_SIZE - PIECE_HEIGHT) // 2
            board_state_img.paste(piece_img, (x, y), piece_img)

    board_state_img.save(output_path)
    print(f"Board image saved to {output_path}")
    return 0


def single_board_generation(fen: str, output_path: str, use_invalid_fen: bool = False) -> int:
    """
    Generate a single chess board image from a FEN string.

    Args:
        fen (str): The FEN string representing the chess position.
        output_path (str): The path to save the generated image.
        use_invalid_fen (bool): If True, use an invalid FEN for testing purposes.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    if not fen or not output_path:
        raise ValueError("FEN string and output path must be provided.")
    
    # Load images
    board_image = Image.open(BOARD_FILE).convert("RGBA")
    piece_images = {
        chess.WHITE: {},
        chess.BLACK: {}
    }
    for color in [chess.WHITE, chess.BLACK]:
        for piece_type in chess.PIECE_TYPES:
            piece_file = SPRITE_DIR + PIECE_IMAGES[color][piece_type]
            png_data = cairosvg.svg2png(url=piece_file, output_width=PIECE_WIDTH, output_height=PIECE_HEIGHT)
            piece_img = Image.open(BytesIO(png_data)).convert("RGBA")
            piece_images[color][piece_type] = piece_img

    # Generate the board image
    try:
        generate_board_image(board_image, piece_images, fen, output_path, use_invalid_fen)
    except ValueError as e:
        print(e)
        return 2
    
    return 0

def multi_board_generation(fen_list_file: str, output_dir: str, use_invalid_fen: bool = False) -> int:
    """
    Generate multiple chess board images from a list of FEN strings.

    Args:
        fen_list_file (str): Path to a text file containing FEN strings, one per line.
        output_dir (str): Directory to save the generated images.
        use_invalid_fen (bool): If True, use invalid FENs for testing purposes

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    if not output_dir:
        print("Output directory must be specified.")
        return 4

    # Load images
    board_image = Image.open(BOARD_FILE).convert("RGBA")
    piece_images = {
        chess.WHITE: {},
        chess.BLACK: {}
    }
    for color in [chess.WHITE, chess.BLACK]:
        for piece_type in chess.PIECE_TYPES:
            piece_file = ASSET_PATH + PIECE_IMAGES[color][piece_type]
            png_data = cairosvg.svg2png(url=piece_file, output_width=PIECE_WIDTH, output_height=PIECE_HEIGHT)
            piece_img = Image.open(BytesIO(png_data)).convert("RGBA")
            piece_images[color][piece_type] = piece_img

    with open(fen_list_file, 'r') as f:
        idx = 0
        for fen in f:
            output_path = f"{output_dir}/board_{idx+1}.png"
            result = generate_board_image(board_image, piece_images, fen.strip(), output_path, use_invalid_fen)
            if result != 0:
                print(f"Failed to generate board for FEN: {fen}")
                return result + 4  # Combine error codes
            idx += 1

    return 0

def generate_singletons(config_data: Dict[str, Any], board_image: Image.Image, piece_images: Dict[chess.Color, Dict[chess.Piece, Image.Image]]) -> int:
    """
    Generate singleton chess board images based on the configuration data.

    Args:
        config_data (dict): Configuration data loaded from YAML.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    if not config_data.get("generate_singles", False):
        print("Skipping singleton generation as per configuration.")
        return 0
    
    for piece, use in config_data.get("piece_singles", {}).items():
        if not use:
            continue

        for color in [chess.WHITE, chess.BLACK]:
            piece_img = piece_images[color][chess.PIECE_SYMBOLS.index(piece.lower())]

            for square in chess.SQUARES:
                row = 7 - (square // 8)
                col = square % 8
                x = col * SQUARE_SIZE + (SQUARE_SIZE - PIECE_WIDTH) // 2
                y = row * SQUARE_SIZE + (SQUARE_SIZE - PIECE_HEIGHT) // 2
                board_state_img = board_image.copy()
                board_state_img.paste(piece_img, (x, y), piece_img)
                output_path = f"{DATA_DIR}/singles/{piece}_{square}.png"
                board_state_img.save(output_path)

    return 0

def generate_predefined(config_data: dict, board_image: Image.Image, piece_images: Dict[chess.Color, Dict[chess.Piece, Image.Image]]) -> int:
    """
    Generate predefined chess board images based on the configuration data.

    Args:
        config_data (dict): Configuration data loaded from YAML.
        board_image (Image.Image): The base image of the chess board.
        piece_images (Dict[chess.Color, Dict[chess.Piece, Image.Image]]): Dictionary of piece images.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    if not config_data.get("used_fens", []):
        print("Skipping predefined generation as per configuration.")
        return 0

    idx = 0
    for fen in config_data["used_fens"]:
        output_path = f"{DATA_DIR}/predefined/board_{idx+1}.png"
        result = generate_board_image(board_image, piece_images, fen.strip(), output_path, True)
        if result != 0:
            print(f"Failed to generate board for FEN: {fen}")
            return result + 2 # Combine error codes
        idx += 1

    return 0

def generate_randoms(config_data: dict, board_image: Image.Image, piece_images: Dict[chess.Color, Dict[chess.Piece, Image.Image]]) -> int:
    """
    Generate random chess board images based on the configuration data.

    Args:
        config_data (dict): Configuration data loaded from YAML.
        board_image (Image.Image): The base image of the chess board.
        piece_images (Dict[chess.Color, Dict[chess.Piece, Image.Image]]): Dictionary of piece images.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """

    random_positions = config_data.get("num_positions", 0)
    used_fens = len(config_data.get("used_fens", []))

    if random_positions <= used_fens:
        print("Already generated enough predefined positions; skipping random generation.")
        return 0

    game_types = config_data.get("endgames", [])
    if not game_types:
        print("No endgame types specified for random generation; skipping.")
        return 0
    
    board = chess.Board()

    for pos_idx in range(random_positions-used_fens):
        board.clear_board()
        game_type = random.choice(game_types)
        
        position_generated = False
        for _ in range(config_data.get("max_attempts")):
            w_pieces, b_pieces = game_type.split("v")
            pieces = [
                *[chess.Piece.from_symbol(p) for p in w_pieces],
                *[chess.Piece.from_symbol(p.lower()) for p in b_pieces]
            ]
            potential_squares = random.sample(chess.SQUARES, len(pieces))

            for piece, square in zip(pieces, potential_squares):
                board.set_piece_at(square, piece)

            # If the configuration is valid, break out of the attempt loop
            if valid_board(board) or not config_data.get("force_valid", True):
                position_generated = True
                break

            # If we couldn't place all pieces, reset the board
            board.clear_board()

        if not position_generated:
            print(f"Failed to generate a valid position for game type {game_type} after {config_data.get('max_attempts')} attempts.")
            return 6  # Error code for failure to generate valid position

        fen = board.fen()
        output_path = f"{DATA_DIR}/random/board_{pos_idx+1}.png"
        result = generate_board_image(board_image, piece_images, fen.strip(), output_path, not config_data.get("force_valid", True))
        if result != 0:
            print(f"Failed to generate random board for FEN: {fen}")
            return result + 2  # Combine error codes
    


def training_data_generation(config_file: str) -> int:
    """
    Generate training data based on the provided configuration file.

    Args:
        config_file (str): Path to the training configuration YAML file.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    
    if not config_file:
        print("Training configuration file must be specified.")
        return 8
    
    if not os.path.isfile(config_file):
        print(f"Configuration file {config_file} does not exist.")
        return 8

    if not os.path.splitext(config_file)[1] in ['.yaml', '.yml']:
        print("Configuration file must be a YAML file.")
        return 8

    board_image = Image.open(BOARD_FILE).convert("RGBA")
    piece_images = {
        chess.WHITE: {},
        chess.BLACK: {}
    }
    for color in [chess.WHITE, chess.BLACK]:
        for piece_type in chess.PIECE_TYPES:
            piece_file = ASSET_PATH + PIECE_IMAGES[color][piece_type]
            png_data = cairosvg.svg2png(url=piece_file, output_width=PIECE_WIDTH, output_height=PIECE_HEIGHT)
            piece_img = Image.open(BytesIO(png_data)).convert("RGBA")
            piece_images[color][piece_type] = piece_img

    with open(config_file, 'r') as f:
        config_data = yaml.safe_load(f)

        if generate_singletons(config_data, board_image, piece_images):
            return 8
        if generate_predefined(config_data, board_image, piece_images):
            return 8
        if generate_randoms(config_data, board_image, piece_images):
            return 8

    return 0

def main(args: argparse.Namespace) -> int:
    """
    Main function to parse arguments and generate the chess board image.
    
    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """

    if args.single:
        return single_board_generation(args.single, args.output_file, args.invalid)
    elif args.from_file:
        return multi_board_generation(args.from_file, args.output_dir, args.invalid)  
    elif args.gen_train_data:
        return training_data_generation(args.train_config)
    else:
        print("No valid operation specified. Use --single, --from-file, or --gen-train-data.")

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate chess board images from FEN strings.")
    parser.add_argument("--single", "-s", type=str, help="Single FEN string representing the chess position.")
    parser.add_argument("--from-file", "-f", type=str, help="Path to a text file containing FEN strings, one per line.")
    parser.add_argument("--output-file", "-o", type=str, help="Output path for a single generated image.")
    parser.add_argument("--output-dir", "-d", type=str, help="Output directory for multiple generated images from a file.")
    parser.add_argument("--invalid", action="store_true", help="Allow generation from invalid FEN strings.")
    parser.add_argument("--gen-train-data", "-g", action="store_true", help="Generate training data based on the train_config.yaml file (found under config/).")
    parser.add_argument("--train-config", "-c", type=str, default="config/train_config.yaml", help="Path to the training configuration YAML file.")
    parser.add_argument("--img-size", "-i", type=int, default=BOARD_WIDTH, help="Size of the generated images (width and height in pixels).")
    sys.exit(main(parser.parse_args()))
