#!/usr/bin/env python3
"""
stegoSTRIPSus.py - Chess Endgame Steganography Solver
Combines YOLO detection with STRIPS planning for chess endgame analysis
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple

from PIL import Image
from ultralytics import YOLO

# Import our package modules
from stegochess import board, model, solver, ChessPredictor


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
    results = model.detect_from_image(image_path)
    fen = model.detection_to_fen(results)
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
    print("  1. train-gen   - Generate training data for YOLO model")
    print("  2. train       - Train YOLO model on generated data")
    print("  3. detect      - Run YOLO detection on chess board image")
    print("  4. generate    - Generate board visualization from FEN string")
    print("  5. solve-fen   - Solve chess endgame from FEN string")
    print("  6. solve-image - Detect board from image and solve endgame")
    print("  7. solve-pred  - Solve a predefined endgame")
    print("  8. list        - List all available predefined endgames")
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
    print("\n[1] Generate training data")
    print("[2] Train YOLO model")
    print("[3] Detect board from image")
    print("[4] Generate board from FEN")
    print("[5] Solve from FEN string")
    print("[6] Solve from image")
    print("[7] Solve predefined endgame")
    print("[8] List predefined endgames")
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

        if choice == '1' or choice == 'train-gen':
            if board.training_data_generation(sprite_dir=board.SPRITE_DIR, board_dir=board.BOARD_DIR):
                print("\n[ERROR] Training data generation failed.")
            else:
                print("\n[TRAIN-GEN] Training data generation completed successfully.")
        
        elif choice == '2' or choice == 'train':
            model.train_model()

        elif choice == '3' or choice == 'detect':
            image_path = input("[DETECT] Enter image path: ").strip()
            if image_path:
                model.detect_board(image_path)
            else:
                print("[ERROR] Image path cannot be empty")

        elif choice == '4' or choice == 'generate':
            fen = input("[GENERATE] Enter FEN string: ").strip()
            if fen:
                board.generate_board(fen)
            else:
                print("[ERROR] FEN string cannot be empty")

        elif choice == '5' or choice == 'solve-fen':
            fen = input("[SOLVE] Enter FEN string: ").strip()
            if fen:
                _ = solver.solve_from_fen(fen)
            else:
                print("[ERROR] FEN string cannot be empty")

        elif choice == '6' or choice == 'solve-image':
            image_path = input("Enter image path: ").strip()
            if image_path:
                _ = solver.solve_from_image(image_path)
            else:
                print("[ERROR] Image path cannot be empty")

        elif choice == '7' or choice == 'solve-pred':
            endgame = input("Enter predefined endgame name or ID: ").strip()
            if endgame:
                solver.solve_predefined(endgame)
            else:
                print("[ERROR] Endgame name cannot be empty")

        elif choice == '8' or choice == 'list':
            solver.list_predefined_endgames()

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
