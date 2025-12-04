#!/usr/bin/env python3
"""
stegoSTRIPSus.py - Chess Endgame Steganography Solver
Combines YOLO detection with STRIPS planning for chess endgame analysis
"""

import sys
from pathlib import Path

# Import our package modules
from stegochess import detection, solver, board


def detect_board(image_path: Path):
    """
    Run YOLO detection on chess board image
    
    Args:
        image_path (Path): Path to the chess board image

    Returns:
        dict: Detected pieces and their positions
    """
    print(f"\n[DETECT] Running detection on image: {image_path}")

    model_path = input("Enter YOLO model path (or press Enter for default 'defaults/best.pt'): ").strip()
    try:
        if not model_path:
            model_path = Path("defaults/best.pt")
        else:
            model_path = Path(model_path)

        if not model_path.exists():
            print(f"[ERROR] Model file does not exist: {model_path}")
            return
    except Exception as e:
        print(f"[ERROR] Invalid model path: {e}")
        return

    results = detection.detect_from_image(image_path, model_path)
    fen = detection.detection_to_fen(results)
    print(f"Detected FEN: {fen}")
    return results


def generate_board(fen_string):
    """Generate board visualization from FEN string"""
    print(f"\n[GENERATE] Generating board from FEN: {fen_string}")
    board.print_board_ascii(fen_string)
    board.generate_board_image(fen_string)


def solve_fen(fen_string):
    """Solve chess endgame from FEN string using STRIPS"""
    print(f"\n[SOLVE] Solving endgame from FEN: {fen_string}")
    solution = solver.solve_from_fen(fen_string)
    if solution:
        print(f"Solution found: {solution}")
    else:
        print("No solution found")
    return solution


def solve_image(image_path):
    """Detect board from image and solve using STRIPS"""
    print(f"\n[SOLVE] Detecting and solving from image: {image_path}")
    # Run detection
    results = detection.detect_from_image(image_path)
    fen = detection.detection_to_fen(results)
    print(f"Detected FEN: {fen}")

    # Solve with STRIPS
    solution = solver.solve_from_fen(fen)
    if solution:
        print(f"Solution found: {solution}")
    else:
        print("No solution found")
    return solution


def solve_predefined(endgame_name):
    """Solve a predefined endgame from solver/predefined/"""
    print(f"\n[SOLVE] Running predefined endgame: {endgame_name}")
    solution = solver.solve_predefined(endgame_name)
    if solution:
        print(f"Solution found: {solution}")
    else:
        print("No solution found")
    return solution


def list_predefined():
    """List all available predefined endgames"""
    print("\n[LIST] Available predefined endgames:")
    endgames = solver.list_predefined_endgames()
    for endgame in endgames:
        print(f"  - {endgame}")
    return endgames


def show_help():
    """Display help information"""
    print("\n" + "="*60)
    print("Chess Endgame Steganography Solver - Help")
    print("="*60)
    print("\nAvailable Commands:")
    print("  1. detect      - Run YOLO detection on chess board image")
    print("  2. generate    - Generate board visualization from FEN string")
    print("  3. solve-fen   - Solve chess endgame from FEN string")
    print("  4. solve-image - Detect board from image and solve endgame")
    print("  5. solve-pred  - Solve a predefined endgame")
    print("  6. list        - List all available predefined endgames")
    print("  h. help        - Show this help message")
    print("  q. quit        - Exit the program")
    print("\nExamples:")
    print("  Predefined endgames: PUSH, POP, ADD, SUB, JMP, JZ, LOAD, HALT")
    print("  FEN example: '7k/8/4Q1K1/8/8/8/8/8 w - - 0 1'")
    print("="*60)


def print_menu():
    """Print the main menu"""
    print("\n" + "="*60)
    print("Chess Endgame Steganography Solver")
    print("="*60)
    print("\n[1] Detect board from image")
    print("[2] Generate board from FEN")
    print("[3] Solve from FEN string")
    print("[4] Solve from image")
    print("[5] Solve predefined endgame")
    print("[6] List predefined endgames")
    print("[h] Help")
    print("[q] Quit")
    print("-"*60)


def main():
    """Main interactive loop"""
    print("\n" + "="*60)
    print("Welcome to stegoSTRIPSus - Chess Endgame Steganography Solver")
    print("YOLO Detection + STRIPS Planning")
    print("="*60)
    print("\nType 'h' for help or 'q' to quit")

    while True:
        print_menu()
        choice = input("\nEnter your choice: ").strip().lower()

        if choice == '1' or choice == 'detect':
            image_path = input("Enter image path: ").strip()
            if image_path:
                try:
                    image_path_obj = Path(image_path)
                    if not image_path_obj.exists():
                        print(f"[ERROR] Image file does not exist: {image_path}")
                        continue

                    detect_board(image_path_obj)
                except Exception as e:
                    print(f"[ERROR] Invalid image path: {e}")
                    continue

            else:
                print("[ERROR] Image path cannot be empty")

        elif choice == '2' or choice == 'generate':
            fen = input("Enter FEN string: ").strip()
            if fen:
                generate_board(fen)
            else:
                print("[ERROR] FEN string cannot be empty")

        elif choice == '3' or choice == 'solve-fen':
            fen = input("Enter FEN string: ").strip()
            if fen:
                solve_fen(fen)
            else:
                print("[ERROR] FEN string cannot be empty")

        elif choice == '4' or choice == 'solve-image':
            image_path = input("Enter image path: ").strip()
            if image_path:
                solve_image(image_path)
            else:
                print("[ERROR] Image path cannot be empty")

        elif choice == '5' or choice == 'solve-pred':
            endgame_name = input("Enter predefined endgame name (PUSH/POP/ADD/SUB/JMP/JZ/LOAD/HALT): ").strip().upper()
            if endgame_name:
                solve_predefined(endgame_name)
            else:
                print("[ERROR] Endgame name cannot be empty")

        elif choice == '6' or choice == 'list':
            list_predefined()

        elif choice == 'h' or choice == 'help':
            show_help()

        elif choice == 'q' or choice == 'quit':
            print("\nДо Свидания :)\n")
            sys.exit(0)

        else:
            print(f"\n[ERROR] Invalid choice: '{choice}'")
            print("Type 'h' for help")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye!\n")
        sys.exit(0)
