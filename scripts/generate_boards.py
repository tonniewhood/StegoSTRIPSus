
import argparse
import os
import random
import sys

from typing import Dict

import chess

from PIL import Image
import shutil


ASSET_PATH = "/home/tonniewhood/School/Fall_2025/CS_5600/Final_Project/assets/"
DATA_DIR = "/home/tonniewhood/School/Fall_2025/CS_5600/Final_Project/datasets/chess_pieces/"
TRAIN_DIR = DATA_DIR + "train/"
VAL_DIR = DATA_DIR + "val/"
BOARD_FILE = ASSET_PATH + "boards/{}.png"
SPRITE_DIR = ASSET_PATH + "sprites/"
PIECE_IMAGES = {
    chess.WHITE: {
        chess.PAWN: "white/{}/pawn.png",
        chess.KNIGHT: "white/{}/knight.png",
        chess.BISHOP: "white/{}/bishop.png",
        chess.ROOK: "white/{}/rook.png",
        chess.QUEEN: "white/{}/queen.png",
        chess.KING: "white/{}/king.png",
    },
    chess.BLACK: {
        chess.PAWN: "black/{}/pawn.png",
        chess.KNIGHT: "black/{}/knight.png",
        chess.BISHOP: "black/{}/bishop.png",
        chess.ROOK: "black/{}/rook.png",
        chess.QUEEN: "black/{}/queen.png",
        chess.KING: "black/{}/king.png",
    }
}

BOARD_WIDTH = 1200
BOARD_HEIGHT = 1200
SQUARE_SIZE = BOARD_WIDTH // 8

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
            x = col * SQUARE_SIZE + (SQUARE_SIZE - piece_img.width) // 2
            y = row * SQUARE_SIZE + (SQUARE_SIZE - piece_img.height) // 2
            board_state_img.paste(piece_img, (x, y), piece_img)

    board_state_img.save(output_path)
    print(f"Board image saved to {output_path}")
    return 0


def single_board_generation(fen: str, output_path: str, use_invalid_fen: bool = False, board_style: str = "green", piece_style: str = "neo") -> int:
    """
    Generate a single chess board image from a FEN string.

    Args:
        fen (str): The FEN string representing the chess position.
        output_path (str): The path to save the generated image.
        use_invalid_fen (bool): If True, use an invalid FEN for testing purposes.
        board_style (str): The style of the chess board to use.
        piece_style (str): The style of the chess pieces to use.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    if not fen or not output_path:
        raise ValueError("FEN string and output path must be provided.")
    
    # Load images
    board_image = Image.open(BOARD_FILE.format(board_style)).convert("RGBA")
    piece_images = {
        chess.WHITE: {},
        chess.BLACK: {}
    }
    for color in [chess.WHITE, chess.BLACK]:
        for piece_type in chess.PIECE_TYPES:
            piece_file = SPRITE_DIR + PIECE_IMAGES[color][piece_type].format(piece_style)
            piece_img = Image.open(piece_file).convert("RGBA")
            piece_images[color][piece_type] = piece_img

    # Generate the board image
    try:
        generate_board_image(board_image, piece_images, fen, output_path, use_invalid_fen)
    except ValueError as e:
        print(e)
        return 2
    
    return 0

def multi_board_generation(fen_list_file: str, output_dir: str, use_invalid_fen: bool = False, board_style: str = "green", piece_style: str = "neo") -> int:
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
    board_image = Image.open(BOARD_FILE.format(board_style)).convert("RGBA")
    piece_images = {
        chess.WHITE: {},
        chess.BLACK: {}
    }
    for color in [chess.WHITE, chess.BLACK]:
        for piece_type in chess.PIECE_TYPES:
            piece_file = ASSET_PATH + PIECE_IMAGES[color][piece_type].format(piece_style)
            piece_img = Image.open(piece_file).convert("RGBA")
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

def save_pieces_with_background(data_dir: str, sprite_style: str, square_img: Image.Image, board_style: str, is_light_square: bool) -> None:
    """
    Save chess piece images with a given square background for training data.

    Args:
        data_dir (str): Directory to save the training data.
        sprite_style (str): Style of the chess pieces.
        square_img (Image.Image): Image of the square background.
        board_style (str): Style of the chess board.
        is_light_square (bool): Whether the square is light or dark.
    """
    square_type = "light" if is_light_square else "dark"
    color_identifiers = {chess.WHITE: "w", chess.BLACK: "b"}
    piece_identifiers = {
        chess.KING: "k",
        chess.QUEEN: "q", 
        chess.BISHOP: "b", 
        chess.KNIGHT: "n", 
        chess.PAWN: "p", 
        chess.ROOK: "r", 
    }

    for color in chess.COLORS:
        for piece in chess.PIECE_TYPES:

            piece_dir = os.path.join(TRAIN_DIR, color_identifiers[color] + piece_identifiers[piece])
            if not os.path.exists(piece_dir):
                os.mkdir(piece_dir)

            piece_file = os.path.join(SPRITE_DIR, PIECE_IMAGES[color][piece].format(sprite_style))
            piece_img = Image.open(piece_file).convert("RGBA")

            # Create a new image with the square background
            combined_img = square_img.copy()
            x = (SQUARE_SIZE - piece_img.width) // 2
            y = (SQUARE_SIZE - piece_img.height) // 2
            combined_img.paste(piece_img, (x, y), piece_img)

            # Save the combined image
            save_path = os.path.join(piece_dir, f"{board_style}_{sprite_style}_{square_type}.png")
            combined_img.save(save_path)
            print(f"Saved training image: {save_path}")

def training_data_generation(sprite_dir: str, board_dir: str) -> int:
    """
    Generate training data based on the assets directory path

    Args:
        sprite_dir (str): Path to the directory containing sprite images.
        board_dir (str): Path to the directory containing board images.

    Returns:
        int: Exit code (0 for success, non-zero for failure).
    """
    
    if not os.path.exists(sprite_dir):
        print(f"Sprite directory '{sprite_dir}' does not exist.")
        return 5
    
    if not os.path.exists(board_dir):
        print(f"Board directory '{board_dir}' does not exist.")
        return 6

    sprite_styles = os.listdir(os.path.join(sprite_dir, "white"))
    board_imgs = []
    board_styles = []
    for board_file in os.listdir(board_dir):
        board_imgs.append(Image.open(os.path.join(board_dir, board_file)).convert("RGBA"))
        board_styles.append(os.path.splitext(board_file)[0])

    light_squares = [
        board.crop((0, 0, SQUARE_SIZE, SQUARE_SIZE))
        for board in board_imgs
    ]
    dark_squares = [
        board.crop((SQUARE_SIZE, 0, 2 * SQUARE_SIZE, SQUARE_SIZE))
        for board in board_imgs
    ]

    if os.path.exists(TRAIN_DIR):
        shutil.rmtree(TRAIN_DIR)
    os.mkdir(TRAIN_DIR)

    if os.path.exists(VAL_DIR):
        shutil.rmtree(VAL_DIR)
    os.mkdir(VAL_DIR)

    empty_dir = os.path.join(TRAIN_DIR, "empty")
    if not os.path.exists(empty_dir):
        os.mkdir(empty_dir)

    for light, dark, board_style in zip(light_squares, dark_squares, board_styles):

        light_square_path = os.path.join(empty_dir, f"{board_style}_light.png")
        if not os.path.exists(light_square_path):
            light.save(light_square_path)
            print(f"Saved empty light square image: {light_square_path}")
        
        dark_square_path = os.path.join(empty_dir, f"{board_style}_dark.png")
        if not os.path.exists(dark_square_path):
            dark.save(dark_square_path)
            print(f"Saved empty dark square image: {dark_square_path}")

        for style in sprite_styles:
            save_pieces_with_background(DATA_DIR, style, light, board_style, is_light_square=True)
            save_pieces_with_background(DATA_DIR, style, dark, board_style, is_light_square=False)

    for piece in os.listdir(TRAIN_DIR):
        images = os.listdir(os.path.join(TRAIN_DIR, piece))
        if not os.path.exists(os.path.join(VAL_DIR, piece)):
            os.mkdir(os.path.join(VAL_DIR, piece))

        val_sample = random.sample(images, max(1, int(0.3 * len(images)))) # 30% for validation

        for img in val_sample:
            src_path = os.path.join(TRAIN_DIR, piece, img)
            dest_path = os.path.join(VAL_DIR, piece, img)
            os.rename(src_path, dest_path)
            print(f"Moved {os.path.basename(src_path)} to validation set")

def main(args: argparse.Namespace) -> int:
    """
    Main function to parse arguments and generate the chess board image.
    
    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        int: Exit code (0 for success, 1 for failure).
    """

    if args.single:
        return single_board_generation(args.single, args.output_file, args.invalid, args.board_style, args.piece_style)
    elif args.from_file:
        return multi_board_generation(args.from_file, args.output_dir, args.invalid)  
    elif args.gen_train_data:
        return training_data_generation(args.sprite_dir, args.board_dir)
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
    parser.add_argument("--sprite-dir", type=str, default="assets/sprites/", help="Path to the directory containing sprite images.")
    parser.add_argument("--board-dir", type=str, default="assets/boards/", help="Path to the directory containing board images.")
    parser.add_argument("--img-size", "-i", type=int, default=BOARD_WIDTH, help="Size of the generated images (width and height in pixels).")
    parser.add_argument("--board-style", "-b", type=str, default="green", help="Style of the chess board to use.")
    parser.add_argument("--piece-style", "-p", type=str, default="neo", help="Style of the chess pieces to use.")
    sys.exit(main(parser.parse_args()))
