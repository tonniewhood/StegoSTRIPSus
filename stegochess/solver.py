"""
solver.py - STRIPS solver interface
"""

import subprocess
from pathlib import Path


def solve_from_fen(fen_string):
    """
    Solve chess endgame from FEN string using STRIPS

    Args:
        fen_string: FEN string representing the board position

    Returns:
        list: Solution moves
    """
    print(f"[SOLVER] Solving FEN: {fen_string}")
    # TODO: Convert FEN to STRIPS world state
    # TODO: Call STRIPS solver via subprocess or FFI
    # TODO: Parse and return solution
    return []


def solve_predefined(endgame_name):
    """
    Solve a predefined endgame

    Args:
        endgame_name: Name of the predefined endgame (PUSH, POP, etc.)

    Returns:
        list: Solution moves
    """
    print(f"[SOLVER] Solving predefined: {endgame_name}")
    # TODO: Load predefined endgame file
    # TODO: Call STRIPS solver
    return []


def list_predefined_endgames():
    """
    List all available predefined endgames

    Returns:
        list: Names of available endgames
    """
    predefined_dir = Path("solver/predefined")
    if not predefined_dir.absolute().exists():
        return []

    # TODO: List and parse predefined endgame files
    return ["PUSH", "POP", "ADD", "SUB", "JMP", "JZ", "LOAD", "HALT"]


def call_strips_solver(world_file, operators_file, goal):
    """
    Call the Lisp STRIPS solver

    Args:
        world_file: Path to the world state file (.wff)
        operators_file: Path to the operators file (.op)
        goal: Goal to achieve

    Returns:
        str: STRIPS solver output
    """
    # TODO: Implement subprocess call to sbcl/clisp with STRIPS
    # Example: subprocess.run(['sbcl', '--load', 'solver.lisp', ...])
    pass
