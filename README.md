# stegoSTRIPSus - Chess Endgame Steganography Solver

A novel steganographic system that encodes programs as chess endgame positions, combining YOLO-based piece detection with STRIPS planning to solve and decode chess puzzles.

---

## Overview

stegoSTRIPSus is a chess endgame steganography solver that uses computer vision (YOLO) to detect chess pieces and AI planning (STRIPS) to find checkmate sequences. Each of 8 predefined endgame positions encodes a different instruction, allowing programs to be hidden in chess board images.

### How It Works

1. **YOLO Detection**: Detects chess pieces from images and converts them to FEN notation
2. **STRIPS Planning**: Uses backward-chaining planning to find optimal checkmate sequences
3. **Steganographic Encoding**: Each endgame position represents a computational instruction

---

## Features

- Chess piece detection using YOLOv8 computer vision
- 8 predefined endgame positions (Byrd, Jim-Bob, Mr-NewVegas, Marston, AERO-X, StegoMate, Pim, Tonniewhood)
- STRIPS-based automated planning for checkmate sequences
- Board generation from FEN strings with customizable styles
- Interactive CLI for all operations
- Training data generation for custom models
- Support for multiple board and piece styles from Chess.com

---

## Prerequisites

- **Python 3.12+**
- **Common Lisp** (CLISP, SBCL, or CCL)
- **pip** (Python package manager)
- Internet connection (for initial asset downloads)

### Installing Common Lisp

**Ubuntu/Debian:**
```bash
sudo apt install clisp
```

**macOS:**
```bash
brew install clisp
```

---

## Installation

### Quick Start

Run the automated setup script:

```bash
chmod +x setup.sh
./setup.sh
```

The script will:
- Check system requirements
- Install Python dependencies
- Create directory structure
- Download default chess assets
- Optionally train the YOLO model
- Verify STRIPS solver

### Manual Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd Final_Project
```

2. **Install Python package:**
```bash
pip install -e .
```

3. **Create directories:**
```bash
mkdir -p assets/{sprites,boards} datasets/chess_pieces/{train,val} models output
```

4. **Download assets:**
```bash
python -c "from stegochess.board import get_pieces, get_boards; get_pieces('neo'); get_boards('green')"
```

5. **Generate training data and train model:**
```bash
python stegoSTRIPSus.py
# Select option [1] Generate training data
# Select option [2] Train YOLO model
```

---

## Usage

### Interactive CLI

Launch the interactive interface:

```bash
python stegoSTRIPSus.py
```

### Menu Options

**[1] Generate training data**
- Creates training images from available board/piece combinations
- Required before training the YOLO model

**[2] Train YOLO model**
- Trains YOLOv8 on generated training data
- Default: 35 epochs, 160x160 images, batch size 32

**[3] Detect board from image**
- Uses YOLO to detect pieces and generate FEN
- Requires trained model

**[4] Generate board from FEN**
- Creates a chess board image from FEN notation
- Customizable board and piece styles

**[5] Solve from FEN string**
- Uses STRIPS to find checkmate sequence
- Requires Common Lisp

**[6] Solve from image**
- Combines detection and solving
- Full pipeline: image → FEN → solution

**[7] Solve predefined endgame**
- Solves one of 8 predefined positions
- Each represents a different instruction

**[8] List predefined endgames**
- Shows available endgame positions

---

## Project Structure

```
Final_Project/
├── stegochess/              # Python package
│   ├── __init__.py
│   ├── board.py            # Board generation and visualization
│   ├── model.py            # YOLO training and detection
│   ├── solver.py           # STRIPS solver interface
│   └── ChessPredictor.py   # Chess piece prediction
├── solver/                  # STRIPS solver (Common Lisp)
│   ├── strips/             # STRIPS engine
│   │   ├── strips.lisp     # Main STRIPS algorithm
│   │   ├── database.lisp   # Fact database
│   │   ├── unify.lisp      # Unification
│   │   └── ...
│   ├── predefined/         # Predefined endgame positions
│   │   ├── endgame0.wff    # Byrd position
│   │   ├── endgame1.wff    # Jim-Bob position
│   │   └── ...
│   ├── endgame.op          # STRIPS operators
│   └── solve.lisp          # CLI wrapper for STRIPS
├── assets/                  # Chess board and piece images
│   ├── sprites/            # Piece images
│   └── boards/             # Board backgrounds
├── datasets/               # Training data for YOLO
│   └── chess_pieces/
│       ├── train/          # Training images
│       └── val/            # Validation images
├── models/                 # Trained YOLO models
│   └── best.pt            # Best model weights
├── output/                 # Generated board images
├── stegoSTRIPSus.py       # Interactive CLI
├── setup.sh               # Automated setup script
├── setup.py               # Python package configuration
└── README.md              # This file
```

---

## How It Works

### YOLO Detection Pipeline

1. **Image Input**: Chess board photograph or screenshot
2. **Piece Detection**: YOLOv8 detects and classifies each piece
3. **Grid Mapping**: Maps detected pieces to board coordinates (a1-h8)
4. **FEN Generation**: Converts board state to Forsyth-Edwards Notation

### STRIPS Planning Pipeline

1. **World State**: FEN converted to FOPC (First-Order Predicate Calculus) facts
2. **Goal**: Checkmate condition
3. **Operators**: Move operators (queen/rook horizontal/vertical/diagonal moves)
4. **Backward Chaining**: STRIPS plans from goal back to initial state
5. **Solution**: Sequence of moves leading to checkmate

#### STRIPS Components

**World State (WFF):**
```lisp
(AT bk H 8)           ; Black king at H8
(AT wk G 6)           ; White king at G6
(AT wp1 E 6)          ; White queen at E6
(TYPE wp1 queen)      ; wp1 is a queen
(COLOR wp1 white)     ; wp1 is white
```

**Operators:**
```lisp
(def-operator MOVE-QUEEN-VERTICAL
  :goal   (AT ?wp ?file ?to-rank)
  :precond ((AT ?wp ?file ?from-rank))
  :filter ((TYPE ?wp queen) (COLOR ?wp white)
           (DIFFERENT ?from-rank ?to-rank))
  :add ((AT ?wp ?file ?to-rank) (CHECK))
  :del ((AT ?wp ?file ?from-rank)))
```

---

## Endgame Definitions

Each endgame position encodes a computational instruction:

| Name | Instruction | Starting Position (FEN) | Winning Sequence |
|------|-------------|------------------------|------------------|
| Byrd | PUSH | `1k6/8/K1R5/8/8/8/8/2R5 w - - 0 1` | RC6→B6, RC1→C8 |
| Jim-Bob | POP | `1k6/8/1KQ5/8/8/8/8/8 w - - 0 1` | QC6→C7, QC7→B7 |
| Mr-NewVegas | ADD | `6k1/8/5R1K/8/8/8/8/5R2 w - - 0 1` | RF6→F8 |
| Marston | SUB | `7k/8/6K1/5R2/8/8/8/8 w - - 0 1` | RF5→F8 |
| AERO-X | JMP | `8/2R5/8/8/8/1K6/8/k7 w - - 0 1` | RC7→C1 |
| StegoMate | JZ | `7k/8/4Q1K1/8/8/8/8/8 w - - 0 1` | QE6→E8 |
| Pim | LOAD | `3Q4/8/k1K5/8/8/8/8/8 w - - 0 1` | QD8→B6 |
| Tonniewhood | HALT | `4Q3/8/5K1k/8/8/8/8/8 w - - 0 1` | QE8→G6 |

---

## Development

### Training with Custom Datasets

1. **Download additional styles**:
```bash
python -c "from stegochess.board import get_pieces, get_boards; \
           get_pieces('wood'); get_boards('brown')"
```

2. **Generate training data**:
```bash
python stegoSTRIPSus.py
# Select [1] Generate training data
```

3. **Train model**:
```bash
python stegoSTRIPSus.py
# Select [2] Train YOLO model
```

---

## Troubleshooting

### Common Lisp Issues

**Problem:** `clisp: command not found`
**Solution:** Install CLISP: `sudo apt install clisp` or `brew install clisp`

**Problem:** STRIPS solver fails to load
**Solution:** Check file paths in `solver/solve.lisp` - they should be relative to project root

**Problem:** `READ: input stream has reached its end`
**Solution:** Debug mode is enabled. Ensure `(strips-debug nil)` in solve.lisp

### YOLO Detection Issues

**Problem:** Low detection accuracy
**Solution:** Train with more epochs, larger batch size, or more diverse training data

**Problem:** `models/best.pt not found`
**Solution:** Train the model first using option [2] in the CLI

**Problem:** Out of memory during training
**Solution:** Reduce batch size in training parameters

### Asset Download Failures

**Problem:** 404 errors when downloading assets
**Solution:** Chess.com may have changed URLs. Check available styles at https://www.chess.com/chess-themes/

**Problem:** SSL certificate errors
**Solution:** Update `requests` library: `pip install --upgrade requests`

---

## Technical Details

### FEN String Format

Forsyth-Edwards Notation describes board position:
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

- Pieces: K=king, Q=queen, R=rook, B=bishop, N=knight, P=pawn
- Uppercase = white, lowercase = black
- Numbers = empty squares
- `/` = next rank

### YOLO Model Architecture

- **Base Model**: YOLOv8n (nano)
- **Input Size**: 160x160 pixels
- **Classes**: 13 (6 white pieces + 6 black pieces + empty square)
- **Training**: 35 epochs, batch size 32
- **Data Augmentation**: Rotation, scaling, color jitter

---

## License & Credits

### License

This project is for educational purposes as part of CS 5600.

### Credits

- **STRIPS Implementation**: Based on classic STRIPS planner from AI literature. The code is a LISP, STRIPS implementation by (Vladimir Kulyukin)[https://engineering.usu.edu/cs/directory/faculty/kulyukin-vladimir] at Utah State University
- **Chess Assets**: Board and piece images from [Chess.com](https://www.chess.com/chess-themes/)
- **YOLO**: Using [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics)
- **Python Chess**: Using [python-chess](https://python-chess.readthedocs.io/)

---
