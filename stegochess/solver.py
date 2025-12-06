"""
solver.py - STRIPS solver interface
"""

import subprocess
from pathlib import Path
from typing import Tuple

from stegochess import model


TEMPLATE_WFF_PATH = Path("solver/endgame_template.wff")
TEMP_WFF_PATH = Path("solver/temp_endgame.wff")
VALID_FENS = [
    "1k6/8/K1R5/8/8/8/8/2R5 w - - 0 1",
    "1k6/8/1KQ5/8/8/8/8/8 w - - 0 1",
    "6k1/8/5R1K/8/8/8/8/5R2 w - - 0 1",
    "7k/8/6K1/5R2/8/8/8/8 w - - 0 1",
    "8/2R5/8/8/8/1K6/8/k7 w - - 0 1",
    "7k/8/4Q1K1/8/8/8/8/8 w - - 0 1",
    "3Q4/8/k1K5/8/8/8/8/8 w - - 0 1",
    "4Q3/8/5K1k/8/8/8/8/8 w - - 0 1"
]
PIECE_MAP = {
    'Q': 'queen',
    'R': 'rook',
}
SOLVER_CMD = ["clisp", "solver/solve.lisp"]
PREDEFINED_ENDGAMES = [
    "Byrd",
    "Jim-Bob",
    "Mr-NewVegas",
    "Marston",
    "AERO-X",
    "StegoMate",
    "Pim",
    "Tonniewhood"
]


def eval_conditionals(template: str, conditions: Tuple[str, ... ]) -> str:
    """
    Evaluate conditional sections in the template string.
    Sections are marked with [[ --CONDITION ]] delimiters.
    Sections begin with `[[` on a line followed by `-- CONDITION`. If the condition is met,
        the section is included; otherwise, it is omitted.
    Sections are ended with `]]` on a line by itself.
    The string is modified in place.

    Args:
        template: The template string with conditionals
        conditions: Tuple of condition strings to include

    Returns:
        The processed string with conditionals evaluated
    """

    lines = template.splitlines()
    output_lines = []
    skip_section = False
    for line in lines:
        if line.strip().startswith('[[') and '--' in line:
            condition = line.strip().split('--')[1].strip()
            skip_section = condition not in conditions
            continue
        elif line.strip() == ']]':
            skip_section = False
            continue

        if not skip_section:
            output_lines.append(line)

    return '\n'.join(output_lines)

def replace_placeholders(template: str, placeholders: dict) -> str:
    """
    Replace placeholders in the template string with actual values.

    Args:
        template: The template string with placeholders
        placeholders: Dictionary of placeholder names to values

    Returns:
        The processed string with placeholders replaced
    """
    for key, value in placeholders.items():
        template = template.replace(f"{{{{ {key} }}}}", str(value))
    return template

def generate_wff_file(fen_string: str, output_path: Path) -> None:
    """
    Generate a WFF file for the given FEN string.

    Args:
        fen_string: FEN string representing the board position
        output_path: Path to save the generated WFF file
    """
    if fen_string not in VALID_FENS:
        print("[ERROR] FEN string not in predefined valid endgames.")
        return
    
    placeholders = {}
    conditions = []
    num_pieces = 0
    rows = fen_string.split(' ')[0].split('/')
    for r, row in enumerate(rows):
        file = 0
        for char in row:
            if char.isdigit():
                file += int(char)
            else:
                if char.isupper():
                    if char == 'K':
                        placeholders[f"WHITE_KING_FILE"] = chr(ord('a') + file).upper()
                        placeholders[f"WHITE_KING_RANK"] = str(8 - r)
                    else:
                        num_pieces += 1
                        placeholders[f"PIECE{num_pieces}_FILE"] = chr(ord('a') + file).upper()
                        placeholders[f"PIECE{num_pieces}_RANK"] = str(8 - r)
                        placeholders[f"PIECE{num_pieces}_TYPE"] = PIECE_MAP.get(char.upper(), 'unknown')
                else:
                    placeholders[f"BLACK_KING_FILE"] = chr(ord('a') + file).upper()
                    placeholders[f"BLACK_KING_RANK"] = str(8 - r)
                file += 1

    if num_pieces == 1:
        placeholders["PIECE2_TYPE"] = "NIL"
        placeholders["PIECE2_COLOR"] = "NIL"
    else:
        conditions.append('TWO_PIECE')
        placeholders["PIECE2_COLOR"] = "white"

    if placeholders.get("PIECE1_TYPE") == 'queen':
        conditions.append('QUEEN')

    with open(TEMPLATE_WFF_PATH, 'r') as template_file:
        wff_content = template_file.read()
    wff_content = eval_conditionals(wff_content, tuple(conditions))
    wff_content = replace_placeholders(wff_content,placeholders)

    with open(output_path, 'w') as output_file:
        output_file.write(wff_content)

def solve_from_fen(fen_string: str) -> None:
    """
    Solve chess endgame from FEN string using STRIPS

    Args:
        fen_string: FEN string representing the board position
    """
    print(f"[SOLVER] Solving endgame from FEN: {fen_string}")
    if fen_string not in VALID_FENS:
        print("[ERROR] FEN string not in predefined valid endgames.")
        return
    
    generate_wff_file(fen_string, TEMP_WFF_PATH)
    call_strips_solver(str(TEMP_WFF_PATH))

    if TEMP_WFF_PATH.exists():
        TEMP_WFF_PATH.unlink()


def solve_from_image(image_path: str) -> None:
    """
    Detect board from image and solve using STRIPS

    Args:
        image_path: Path to the chess board image
    """

    predicted_fen = model.detect_board(image_path)
    if predicted_fen is None:
        print("[SOLVER] Detection failed, cannot solve.")
        return
    solve_from_fen(predicted_fen)


def solve_predefined(endgame_name):
    """
    Solve a predefined endgame

    Args:
        endgame_name: Name of the predefined endgame (PUSH, POP, etc.)
    """
    print(f"[SOLVER] Solving predefined: {endgame_name}")
    if endgame_name not in PREDEFINED_ENDGAMES and not endgame_name.isdigit():
        print("[ERROR] Invalid predefined endgame name or ID.")
        return
    
    if endgame_name.isdigit():
        endgame_number = int(endgame_name)
    else:
        endgame_number = PREDEFINED_ENDGAMES.index(endgame_name) + 1

    call_strips_solver(f"solver/predefined/endgame{endgame_number}.wff")


def list_predefined_endgames():
    """
    List all available predefined endgames
    """

    print("\n[LIST] Available predefined endgames:")
    for idx, endgame in enumerate(PREDEFINED_ENDGAMES):
        print(f"  - {endgame:<11} ({idx+1}) => FEN: {VALID_FENS[idx]}")


def call_strips_solver(endgame_wff_path: str) -> None:
    """
    Call the Lisp STRIPS solver
    
    Args:
        endgame_wff_path: Path to the WFF file for the endgame
    """
    cmd = SOLVER_CMD + [str(endgame_wff_path)]
    ret_status = subprocess.run(cmd, capture_output=True, text=True)
    if ret_status.returncode != 0:
        print(f"[ERROR] STRIPS solver failed: {ret_status.stderr}")
        return
    
    plan = []
    start_parsing = False
    for line in ret_status.stdout.splitlines():
        if line.startswith("[STRIPS]"):
            print(line)
        elif line == "===BEGIN_PLAN===":
            start_parsing = True
        elif line == "===END_PLAN===":
            start_parsing = False
        elif start_parsing:
            plan.append(line.strip())

    print("\n[SOLVER] Solution Plan:")
    if plan:
        for step in plan:
            print(f"  - {step}")
    else:
        print("No solution found")
