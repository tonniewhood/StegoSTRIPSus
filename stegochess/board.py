"""
board.py - Chess board representation and visualization
"""

import os
import random
import requests
import shutil
from typing import Dict

import chess
from PIL import Image

CHESS_THEME_URL = "https://www.chess.com/chess-themes/"
PIECE_BASE_URL = CHESS_THEME_URL + "pieces/{}/{}/{}{}.png"
BOARD_BASE_URL = "https://images.chesscomfiles.com/chess-themes/boards/{}/150.png"
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


def generate_board_image(board_image: Image.Image, piece_images: Dict[chess.Color, Dict[chess.PieceType, Image.Image]], fen: str, use_invalid_fen: bool = False) -> Image.Image:
    """
    Generate a chess board image from a FEN string and save it to the specified output path.

    Args:
        board_image (Image.Image): The base image of the chess board.
        piece_images (List[Image.Image]): List of piece images indexed by color and piece type.
        fen (str): The FEN string representing the chess position.
        output_path (str): The path to save the generated image.
        use_invalid_fen (bool): If True, use an invalid FEN for testing purposes.

    Returns:
        Image.Image: The generated board state image.
    """

    try:
        board = chess.Board(fen)
        if not valid_board(board):
            if not use_invalid_fen:
                return None
            print("WARNING: Input FEN string is invalid. Proceeding due to request.")
    except ValueError:
        if not use_invalid_fen:
            return None
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


    return board_state_img


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
        board_state_img = generate_board_image(board_image, piece_images, fen, use_invalid_fen)
        if board_state_img is None:
            return 1
        board_state_img.save(output_path)
        print(f"Board image saved to {output_path}")
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
            board_state_img = generate_board_image(board_image, piece_images, fen.strip(), use_invalid_fen)
            if board_state_img is None:
                print(f"Failed to generate board for FEN: {fen}")
                return 1
            board_state_img.save(output_path)
            print(f"Board image saved to {output_path}")
            idx += 1

    return 0

def save_pieces_with_background(sprite_style: str, square_img: Image.Image, board_style: str, is_light_square: bool) -> None:
    """
    Save chess piece images with a given square background for training data.

    Args:
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

def get_pieces(set_name: str, save_dir: str, piece_size: int) -> None:
    """
    Download chess piece images from Chess.com and save them to the specified directory.

    Args:
        set_name (str): The name of the chess piece set to download.
        save_dir (str): The directory where the images will be saved.
        piece_size (int): The size of the chess piece images to download. (Will be square)
    """

    if not os.path.exists(save_dir):
        option = input(f"Directory '{save_dir}' does not exist. Create it? [y/n]: ")
        if option.lower().startswith('y'):
            os.makedirs(save_dir)
        else:
            print("Aborting download.")
            return
        
    colors = ['white', 'black']
    pieces = {'king': 'k', 'queen': 'q', 'rook': 'r', 'bishop': 'b', 'knight': 'n', 'pawn': 'p'}

    for color in colors:
        for piece in pieces:
            piece_url = PIECE_BASE_URL.format(set_name, piece_size, color[0].lower(), pieces[piece])
            response = requests.get(piece_url)
            if response.status_code == 200:
                file_dir = os.path.join(save_dir, color, set_name)
                os.makedirs(file_dir, exist_ok=True)
                file_path = os.path.join(file_dir, f"{piece}.png")
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded {file_path}")
            else:
                print(f"Failed to download {piece_url}: Status code {response.status_code}")

def get_boards(set_name: str, save_dir: str) -> None:
    """
    Download chess board images from Chess.com and save them to the specified directory.

    Args:
        set_name (str): The name of the chess board set to download.
        save_dir (str): The directory where the images will be saved.
    """

    if not os.path.exists(save_dir):
        option = input(f"Directory '{save_dir}' does not exist. Create it? [y/n]: ")
        if option.lower().startswith('y'):
            os.makedirs(save_dir)
        else:
            print("Aborting download.")
            return

    board_url = BOARD_BASE_URL.format(set_name)
    response = requests.get(board_url)
    if response.status_code == 200:
        file_path = os.path.join(save_dir, f"{set_name}.png")
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {file_path}")
    else:
        print(f"Failed to download {board_url}: Status code {response.status_code}")

def fen_to_board(fen_string):
    """
    Parse FEN string to board representation

    Args:
        fen_string: FEN string

    Returns:
        dict: Board representation with piece positions
    """
    print(f"[BOARD] Parsing FEN: {fen_string}")
    # TODO: Parse FEN string
    return {}


def generate_board_image(fen_string, output_path=None):
    """
    Generate a visual representation of the board from FEN

    Args:
        fen_string: FEN string
        output_path: Optional path to save the image

    Returns:
        str: Path to generated image or display inline
    """
    print(f"[BOARD] Generating board visualization")
    # TODO: Generate board image (using python-chess, PIL, etc.)
    pass


def print_board_ascii(fen_string):
    """
    Print ASCII representation of the board

    Args:
        fen_string: FEN string
    """
    print(f"[BOARD] ASCII representation of: {fen_string}")
    # TODO: Print ASCII board
    print("  a b c d e f g h")
    print("8 . . . . . . . k 8")
    print("7 . . . . . . . . 7")
    print("6 . . . . Q . K . 6")
    print("5 . . . . . . . . 5")
    print("4 . . . . . . . . 4")
    print("3 . . . . . . . . 3")
    print("2 . . . . . . . . 2")
    print("1 . . . . . . . . 1")
    print("  a b c d e f g h")

if __name__ == "__main__":
    raise NotImplementedError("This module is intended to be imported, not run directly.")
