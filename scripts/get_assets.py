
import argparse
import os
import requests


CHESS_THEME_URL = "https://www.chess.com/chess-themes/"
PIECE_BASE_URL = CHESS_THEME_URL + "pieces/{}/{}/{}{}.png"
BOARD_BASE_URL = "https://images.chesscomfiles.com/chess-themes/boards/{}/150.png"

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download chess piece images from Chess.com.")
    parser.add_argument("piece_sets", type=str, help="The name of the chess piece sets to download. (Comma-separated for multiple sets)")
    parser.add_argument("board_sets", type=str, help="The name of the chess board sets to download. (Comma-separated for multiple sets)")
    parser.add_argument("save_dir", type=str, help="The directory where the images will be saved.")
    parser.add_argument("--piece-size", type=int, default=122, help="The size of the chess piece images to download. (Default: 64)")

    args = parser.parse_args()
    piece_sets = [s.strip() for s in args.piece_sets.split(",")]
    board_sets = [s.strip() for s in args.board_sets.split(",")]
    for set_name in piece_sets:
        get_pieces(set_name, os.path.join(args.save_dir, "sprites"), args.piece_size)
    for set_name in board_sets:
        get_boards(set_name, os.path.join(args.save_dir, "boards"))

