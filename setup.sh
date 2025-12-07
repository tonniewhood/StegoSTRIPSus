#!/bin/bash
###############################################################################
# setup.sh - stegoSTRIPSus Project Setup Script
#
# This script automates the setup process for the stegoSTRIPSus chess endgame
# steganography solver project.
#
# Supports: Linux and macOS (Windows via WSL)
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}\n"
}

print_success() {
    echo -e "${GREEN}${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}${NC} $1"
}

print_error() {
    echo -e "${RED}${NC} $1"
}

print_info() {
    echo -e "${BLUE}${NC} $1"
}

###############################################################################
# 1. System Requirements Check
###############################################################################

print_header "Checking System Requirements"

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 12 ]; then
        print_success "Python $PYTHON_VERSION found"
        PYTHON_CMD="python3"
    else
        print_warning "Python $PYTHON_VERSION found, but 3.12+ recommended"
        PYTHON_CMD="python3"
    fi
else
    print_error "Python 3 not found. Please install Python 3.12+"
    exit 1
fi

# Check for Common Lisp implementation
LISP_FOUND=false
LISP_CMD=""

if command -v clisp &> /dev/null; then
    print_success "CLISP found: $(clisp --version | head -n1)"
    LISP_CMD="clisp"
    LISP_FOUND=true
elif command -v sbcl &> /dev/null; then
    print_success "SBCL found: $(sbcl --version)"
    LISP_CMD="sbcl"
    LISP_FOUND=true
elif command -v ccl &> /dev/null; then
    print_success "CCL found"
    LISP_CMD="ccl"
    LISP_FOUND=true
else
    print_warning "No Common Lisp implementation found (CLISP, SBCL, or CCL)"
    print_info "Install one with: sudo apt install clisp (or brew install clisp on macOS)"
    read -p "Continue without Lisp? (STRIPS solver will not work) [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check pip
if command -v pip3 &> /dev/null; then
    print_success "pip3 found"
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    print_success "pip found"
    PIP_CMD="pip"
else
    print_error "pip not found. Please install pip"
    exit 1
fi

###############################################################################
# 2. Python Environment Setup
###############################################################################

print_header "Setting Up Python Environment"

# Ask about virtual environment
read -p "Create a virtual environment? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ ! -d "venv" ]; then
        print_info "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_info "Virtual environment already exists"
    fi

    print_info "Activating virtual environment..."
    source venv/bin/activate
    print_success "Virtual environment activated"
    PIP_CMD="pip"
fi

# Install package in editable mode
print_info "Installing stegochess package in editable mode (This may take awhile, ultralytics is considered 'un-small')..."
$PIP_CMD install -e . --quiet
print_success "Package installed"

print_info "Installing Python dependencies..."
$PIP_CMD install -q Pillow chess ultralytics requests
print_success "Dependencies installed"

###############################################################################
# 3. Directory Structure Creation
###############################################################################

print_header "Creating Directory Structure"

mkdir -p assets/sprites/white
mkdir -p assets/sprites/black
mkdir -p assets/boards
mkdir -p datasets/chess_pieces/train
mkdir -p datasets/chess_pieces/val
mkdir -p models
mkdir -p output

print_success "Created assets/sprites/"
print_success "Created assets/boards/"
print_success "Created datasets/chess_pieces/train/"
print_success "Created datasets/chess_pieces/val/"
print_success "Created models/"
print_success "Created output/"

###############################################################################
# 4. Asset Downloads
###############################################################################

print_header "Downloading Chess Assets"

# Download default assets using Python
print_info "Downloading default piece set (neo)..."
$PYTHON_CMD -c "from stegochess.board import get_pieces; get_pieces('neo', quiet=True)" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "Default piece set downloaded"
else
    print_warning "Failed to download piece set. You can download manually later."
fi

print_info "Downloading default board style (green)..."
$PYTHON_CMD -c "from stegochess.board import get_boards; get_boards('green', quiet=True)" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "Default board style downloaded"
else
    print_warning "Failed to download board style. You can download manually later."
fi

# Ask about additional styles
read -p "Download additional board/piece styles? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Available piece styles: neo, wood, metal, alpha, bases, book, 8_bit, etc."
    read -p "Enter piece style names (comma-separated, or press Enter to skip): " PIECE_STYLES
    if [ ! -z "$PIECE_STYLES" ]; then
        IFS=',' read -ra STYLES <<< "$PIECE_STYLES"
        for style in "${STYLES[@]}"; do
            style=$(echo "$style" | xargs)  # Trim whitespace
            print_info "Downloading piece style: $style"
            $PYTHON_CMD -c "from stegochess.board import get_pieces; get_pieces('$style')" 2>/dev/null && \
                print_success "Downloaded $style" || \
                print_warning "Failed to download $style"
        done
    fi

    print_info "Available board styles: green, brown, blue, gray, purple, etc."
    read -p "Enter board style names (comma-separated, or press Enter to skip): " BOARD_STYLES
    if [ ! -z "$BOARD_STYLES" ]; then
        IFS=',' read -ra STYLES <<< "$BOARD_STYLES"
        for style in "${STYLES[@]}"; do
            style=$(echo "$style" | xargs)  # Trim whitespace
            print_info "Downloading board style: $style"
            $PYTHON_CMD -c "from stegochess.board import get_boards; get_boards('$style')" 2>/dev/null && \
                print_success "Downloaded $style" || \
                print_warning "Failed to download $style"
        done
    fi
fi

###############################################################################
# 5. YOLO Model Setup
###############################################################################

print_header "Setting Up YOLO Model"

if [ -f "models/best.pt" ]; then
    print_success "Pre-trained YOLO model found at models/best.pt"
else
    print_warning "No pre-trained YOLO model found"
    echo ""
    print_info "You can either:"
    print_info "  1. Train the model now (requires assets and takes time)"
    print_info "  2. Train later using the CLI menu option"
    echo ""
    read -p "Train YOLO model now? [y/N]: " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Generating training data..."
        print_warning "This will create training images from all available board/piece combinations"
        $PYTHON_CMD -c "from stegochess.board import training_data_generation, SPRITE_DIR, BOARD_DIR; training_data_generation(SPRITE_DIR, BOARD_DIR)"

        if [ $? -eq 0 ]; then
            print_success "Training data generated"

            print_info "Training YOLO model (this may take a while)..."
            print_info "Training with: epochs=35, imgsz=160, batch=32"
            $PYTHON_CMD -c "from stegochess.model import train_model; train_model(epochs=35, imgsz=160, batch=32)"

            if [ $? -eq 0 ]; then
                print_success "YOLO model trained successfully"
            else
                print_warning "Model training encountered issues. Check logs above."
            fi
        else
            print_warning "Training data generation failed"
        fi
    else
        print_info "Skipping training. You can train later using:"
        print_info "  python stegoSTRIPSus.py -> Option 1 (Generate training data)"
        print_info "  python stegoSTRIPSus.py -> Option 2 (Train YOLO model)"
    fi
fi

###############################################################################
# 6. Common Lisp Setup Verification
###############################################################################

if [ "$LISP_FOUND" = true ]; then
    print_header "Verifying STRIPS Solver"

    print_info "Testing STRIPS solver with predefined endgame..."

    # Test with a predefined endgame
    TEST_OUTPUT=$($LISP_CMD solver/solve.lisp solver/predefined/endgame1.wff 2>&1)

    if echo "$TEST_OUTPUT" | grep -q "BEGIN_PLAN"; then
        print_success "STRIPS solver working correctly"
        print_info "Sample plan output:"
        echo "$TEST_OUTPUT" | sed -n '/BEGIN_PLAN/,/END_PLAN/p' | head -5
    else
        print_warning "STRIPS solver test completed with warnings. Check solver/solve.lisp"
    fi
else
    print_warning "Skipping STRIPS verification (no Lisp implementation found)"
fi

###############################################################################
# 7. Final Verification and Success Message
###############################################################################

print_header "Setup Complete!"

echo -e "${GREEN}✓ Installation successful!${NC}\n"

print_info "Next steps:"
echo "  1. Run the interactive CLI:"
echo "     ${BLUE}python stegoSTRIPSus.py${NC}"
echo ""
echo "  2. Try detecting a board:"
echo "     Use option [3] Detect board from image"
echo ""
echo "  3. Generate a board from FEN:"
echo "     Use option [4] Generate board from FEN"
echo ""
echo "  4. Solve a predefined endgame:"
echo "     Use option [7] Solve predefined endgame"
echo ""

if [ "$LISP_FOUND" = false ]; then
    print_warning "Remember: Install a Common Lisp implementation to use the STRIPS solver"
fi

if [ ! -f "models/best.pt" ]; then
    print_warning "Remember: Train the YOLO model before using detection features"
fi
