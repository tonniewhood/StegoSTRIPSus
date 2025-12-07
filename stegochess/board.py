"""
board.py - Chess board representation and visualization
"""

import os
import random
import requests
import shutil
from typing import Dict, List, Tuple

import chess
from PIL import Image, ImageChops

CHESS_THEME_URL = "https://www.chess.com/chess-themes/"
PIECE_BASE_URL = CHESS_THEME_URL + "pieces/{}/{}/{}{}.png"
BOARD_BASE_URL = "https://images.chesscomfiles.com/chess-themes/boards/{}/150.png"
ASSET_PATH = "assets/"
DATA_DIR = "datasets/chess_pieces/"
TRAIN_DIR = DATA_DIR + "train/"
VAL_DIR = DATA_DIR + "val/"
SPRITE_DIR = ASSET_PATH + "sprites/"
BOARD_DIR = ASSET_PATH + "boards/"
BOARD_FILE = BOARD_DIR + "{}.png"
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

MOVEMENT_FRAMES = 10 # Number of frames for piece movement animation
PIECE_MOVE = Tuple[str, str, str] # (piece_type, from_square, to_square)
CHECKMATE_GRADIENT_PATH = ASSET_PATH + "checkmate_gradient.png"

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
        use_invalid_fen (bool): If True, use an invalid FEN for testing purposes.

    Returns:
        Image.Image: The generated board state image.
    """

    try:
        board = chess.Board(fen)
        if not valid_board(board):
            if not use_invalid_fen:
                return None
            print("[WARNING] Input FEN string is invalid. Proceeding due to request.")
    except ValueError:
        if not use_invalid_fen:
            return None
        print("[WARNING] Input FEN string is invalid. Proceeding due to request.")

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

def create_board_and_piece_images(board_style: str, piece_style: str) -> Tuple[Image.Image, Dict[chess.Color, Dict[chess.PieceType, Image.Image]]]:
    """
    Create board and piece images based on the specified styles.

    Args:
        board_style (str): The style of the chess board to use.
        piece_style (str): The style of the chess pieces to use.

    Returns:
        Tuple[Image.Image, Dict[chess.Color, Dict[chess.PieceType, Image.Image]]]: The board image and piece images.
    """
    # Load board image
    board_image = Image.open(BOARD_FILE.format(board_style)).convert("RGBA")

    # Load piece images
    piece_images = {
        chess.WHITE: {},
        chess.BLACK: {}
    }
    for color in [chess.WHITE, chess.BLACK]:
        for piece_type in chess.PIECE_TYPES:
            piece_file = SPRITE_DIR + PIECE_IMAGES[color][piece_type].format(piece_style)
            piece_img = Image.open(piece_file).convert("RGBA")
            piece_images[color][piece_type] = piece_img

    return board_image, piece_images

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

    if not os.path.exists(os.path.join("output")):
        print("[WARNING] Output directory does not exist. The project may not be setup properly. Ensure you've run `setup.sh`, Creating now.")
        os.makedirs(os.path.join("output"))
    
    # Load images
    board_image, piece_images = create_board_and_piece_images(board_style, piece_style)

    # Generate the board image
    try:
        board_state_img = generate_board_image(board_image, piece_images, fen, use_invalid_fen)
        if board_state_img is None:
            return 1
        board_state_img.save(os.path.join("output", output_path))
        print(f"[GENERATE] Board image saved to {os.path.join('output', output_path)}")
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
    board_image, piece_images = create_board_and_piece_images(board_style, piece_style)

    with open(fen_list_file, 'r') as f:
        idx = 0
        for fen in f:
            output_path = f"{output_dir}/board_{idx+1}.png"
            board_state_img = generate_board_image(board_image, piece_images, fen.strip(), use_invalid_fen)
            if board_state_img is None:
                print(f"Failed to generate board for FEN: {fen}")
                return 1
            board_state_img.save(os.path.join('output', output_path))
            print(f"Board image saved to {os.path.join('output', output_path)}")
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
            save_pieces_with_background(style, light, board_style, is_light_square=True)
            save_pieces_with_background(style, dark, board_style, is_light_square=False)

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

def get_pieces(set_name: str, quiet: bool = False) -> bool:
    """
    Download chess piece images from Chess.com and save them to the specified directory.

    Args:
        set_name (str): The name of the chess piece set to download.
        quiet (bool): If True, suppress output messages.
    
    Return:
        bool: True if download was successful, False otherwise.
    """

    if not os.path.exists(SPRITE_DIR):
        if not quiet:
            print("[WARNING] Sprite asset directory does not exist. The project may not be setup correctly. Ensure you've run `setup.sh`. Creating directory now.")
        os.makedirs(SPRITE_DIR)
        
    colors = ['white', 'black']
    pieces = {'king': 'k', 'queen': 'q', 'rook': 'r', 'bishop': 'b', 'knight': 'n', 'pawn': 'p'}

    for color in colors:
        for piece in pieces:
            piece_url = PIECE_BASE_URL.format(set_name, SQUARE_SIZE, color[0].lower(), pieces[piece])
            response = requests.get(piece_url)
            if response.status_code == 200:
                file_dir = os.path.join(SPRITE_DIR, color, set_name)
                os.makedirs(file_dir, exist_ok=True)
                file_path = os.path.join(file_dir, f"{piece}.png")
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                if not quiet:
                    print(f"[FETCH] Downloaded {file_path}")
            else:
                print(f"[ERROR] Failed to download {piece_url}: Status code {response.status_code}")
                return False
            
    return True

def get_boards(set_name: str, quiet: bool = False) -> bool:
    """
    Download chess board images from Chess.com and save them to the specified directory.

    Args:
        set_name (str): The name of the chess board set to download.
        quiet (bool): If True, suppress output messages.

    Returns:
        bool: True if download was successful, False otherwise.
    """

    if not os.path.exists(BOARD_DIR):
        print("[WARNING] Board asset directory does not exist. The project may not be setup correctly. Ensure you've run `setup.sh`. Creating directory now.")
        os.makedirs(BOARD_DIR)

    board_url = BOARD_BASE_URL.format(set_name)
    response = requests.get(board_url)
    if response.status_code == 200:
        file_path = os.path.join(BOARD_DIR, f"{set_name}.png")
        with open(file_path, 'wb') as f:
            f.write(response.content)
        if not quiet:
            print(f"[FETCH] Downloaded {file_path}")
    else:
        print(f"[ERROR] Failed to download {board_url}: Status code {response.status_code}")
        return False
    
    return True

def list_available_piece_styles() -> Tuple[str, ...]:
    """
    List available chess piece sets under the local assets directory.

    Returns:
        Tuple[str, ...]: A tuple of available piece set names.
    """

    if not os.path.exists(SPRITE_DIR):
        print("[WARNING] Sprite asset directory does not exist. The project may not be setup correctly. Ensure you've run `setup.sh`.")
        return ()
    
    piece_sets = set()
    for files in os.listdir(os.path.join(SPRITE_DIR, "black")):
        set_name, _ = os.path.splitext(files)
        piece_sets.add(set_name)
    
    return tuple(piece_sets)

def list_available_board_styles() -> Tuple[str, ...]:
    """
    List available chess board styles under the local assets directory.

    Returns:
        Tuple[str, ...]: A tuple of available board style names.
    """

    if not os.path.exists(BOARD_DIR):
        print("[WARNING] Board asset directory does not exist. The project may not be setup correctly. Ensure you've run `setup.sh`.")
        return ()
    
    board_styles = []
    for board_file in os.listdir(BOARD_DIR):
        style_name, _ = os.path.splitext(board_file)
        board_styles.append(style_name)
    
    return tuple(board_styles)

def print_board_ascii(fen_string):
    """
    Print ASCII representation of the board

    Args:
        fen_string: FEN string
    """

    print(f"[BOARD] ASCII representation of: {fen_string}")
    ranks = fen_string.split(' ')[0].split('/')
    ascii_board = "\n\t  a b c d e f g h\n"
    for idx, rank in enumerate(ranks):
        ascii_board += f"\t{8 - idx} "
        for char in rank:
            if char.isdigit():
                ascii_board += '. ' * int(char)
            else:
                ascii_board += char + ' '
        ascii_board += "\n"
    print(ascii_board)

def generate_board(fen_string: str) -> None:
    """Generate board visualization from FEN string"""

    print(f"[GENERATE] Generating board from FEN: {fen_string}")
    response = input("[GENERATE] View board ASCII? (y/n): ").strip().lower()
    if response == 'y':
        print_board_ascii(fen_string)

    board_style = input("[GENERATE] Enter board style (default 'green'): ").strip()
    if not board_style:
        board_style = 'green'

    available_boards = list_available_board_styles()
    if board_style not in available_boards:
        fetch_choice = input(f"[GENERATE] Board style '{board_style}' not found locally. Fetch from online [Chess.com]? (y/n): ").strip().lower()
        if fetch_choice == 'y':
            success = get_boards(board_style)
            if not success:
                print(f"[GENERATE] Failed to fetch board style '{board_style}'. Using default 'green'.")
                board_style = 'green'
                if board_style not in available_boards:
                    get_boards(board_style, quiet=True)
        else:
            print(f"[GENERATE] Using default board style 'green'.")
            board_style = 'green'
    
    piece_style = input("[GENERATE] Enter piece style (default 'neo'): ").strip()
    if not piece_style:
        piece_style = 'neo'

    available_pieces = list_available_piece_styles()
    if piece_style not in available_pieces:
        fetch_choice = input(f"[GENERATE] Piece style '{piece_style}' not found locally. Fetch from online [Chess.com]? (y/n): ").strip().lower()
        if fetch_choice == 'y':
            success = get_pieces(piece_style)
            if not success:
                print(f"[GENERATE] Failed to fetch piece style '{piece_style}'. Using default 'neo'.")
                piece_style = 'neo'
                if piece_style not in available_pieces:
                    get_pieces(piece_style, quiet=True)
        else:
            print(f"[GENERATE] Using default piece style 'neo'.")
            piece_style = 'neo'

    board_path = input("[GENERATE] Enter output board image path (default 'generated_board.png'): ").strip()
    if not board_path:
        board_path = "generated_board.png"
    return single_board_generation(fen_string, board_path, use_invalid_fen=True, board_style=board_style, piece_style=piece_style)

def animate_from_fen(output_filename: str, game_board: chess.Board, moves: List[PIECE_MOVE], delay: float = 1.0, smooth_movement: bool = False, loop: bool = False, final_frame_hold: float = 2.0) -> None:
    """
    Animate a sequence of chess board states from FEN strings.

    Args:
        output_filename (str): Path to save the output animation.
        board_states (Tuple[str, ...]): Tuple of FEN strings representing board states.
        delay (float): Delay between frames in seconds.
        smooth_movement (bool): Whether to animate smooth piece movement.
        loop (bool): Whether to loop the animation.
        final_frame_hold (float): Hold time for the final frame in seconds.
    """

    board_style = input("[ANIMATE] Enter board style (default 'green'): ").strip().lower()
    if not board_style:
        board_style = 'green'
    elif board_style not in list_available_board_styles():
        print(f"[ANIMATE] Board style '{board_style}' not found locally. Using default 'green'.")
        board_style = 'green'

    piece_style = input("[ANIMATE] Enter piece style (default 'neo'): ").strip().lower()
    if not piece_style:
        piece_style = 'neo'
    elif piece_style not in list_available_piece_styles():
        print(f"[ANIMATE] Piece style '{piece_style}' not found locally. Using default 'neo'.")
        piece_style = 'neo'

    board_image, piece_images = create_board_and_piece_images(board_style, piece_style)
    checkmate_img = Image.open(CHECKMATE_GRADIENT_PATH).convert("RGBA").resize((SQUARE_SIZE, SQUARE_SIZE))
    frames = [generate_board_image(board_image, piece_images, game_board.fen(), use_invalid_fen=True)]
    for move in moves:
        # Convert move tuple (piece_type, from_square, to_square) to UCI format (from_square + to_square)
        print(move)
        uci_move = f"{move[1].lower()}{move[2].lower()}"
        print(f"[ANIMATE] Applying move: {uci_move}")
        game_board.push_uci(uci_move)
        frame = generate_board_image(board_image, piece_images, game_board.fen(), use_invalid_fen=True)
        if frame is None:
            print(f"[ANIMATE] Failed to generate board for FEN: {game_board.fen()}")
            return
        if smooth_movement:
            print("[ANIMATE] Smooth movement not yet implemented.")
        frames.append(frame)

    king_pos = game_board.king(chess.BLACK)
    king_x, king_y = king_pos % 8, 7 - (king_pos // 8)
    king_alpha = piece_images[chess.BLACK][chess.KING].split()[-1]
    inverted_mask = ImageChops.invert(king_alpha)
    checkmate_img.putalpha(ImageChops.multiply(checkmate_img.split()[3], inverted_mask))
    frames[-1].paste(
        checkmate_img,
        (king_x * SQUARE_SIZE, king_y * SQUARE_SIZE),
        checkmate_img,
    )

    print("Frames: ", len(frames))
    print("Moves: ", moves)

    # Save as GIF
    frames[0].save(
        os.path.join("output", output_filename),
        save_all=True,
        append_images=frames[1:],
        duration=[int(delay * 1000)] * (len(frames) - 1) + [int(final_frame_hold * 1000)],
        loop=0 if loop else 1,
        optimize=True
    )

if __name__ == "__main__":
    raise NotImplementedError("This module is intended to be imported, not run directly.")
