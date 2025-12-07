"""
model.py - Model definitions and utilities for StegoChess
"""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Tuple

from PIL import Image
from torch.cuda import is_available as cuda_is_available
from ultralytics import YOLO

from stegochess import board, ChessPredictor


CLASS_NAMES = ["bb", "bk", "bn", "bp", "bq", "br", "empty", "wb", "wk", "wn", "wp", "wq", "wr"]


def load_model() -> Tuple[YOLO, str]:
    """
    Load a YOLO model for chess piece detection.

    Returns:
        Loaded YOLO model
    """

    model_type = input("[TRAIN] Enter the YOLO version/model type (Default 'yolov8n-cls.pt'): ").strip()
    if not model_type:
        model_type = "yolov8n-cls.pt"

    # Initialize new model from ultralytics hub
    try:
        model = YOLO(model_type)
        print(f"[TRAIN] Initialized model: {model_type} (downloaded from ultralytics)")
    except Exception as e:
        print(f"[ERROR] Failed to initialize model: {e}")
        return None

    return model, model_type.split('.')[0]

def update_dataset_config() -> None:
    """Creates a YAML configuration file for the dataset if it doesn't exist."""

    dataset_path = Path(board.DATA_DIR)
    config_path = Path(board.DATA_DIR) / "data.yaml"
    if not config_path.exists():
        print("[WARNING] `data.yaml` not found in dataset directory. The project may not be setup correctly. Ensure you've run `setup.sh`. Creating `data.yaml` now.")

        with open(config_path, 'w') as f:
            yaml.safe_dump({
                'path': str(dataset_path.absolute()),
                'train': str((dataset_path / "train").absolute()),
                'val': str((dataset_path / "val").absolute()),
                'nc': len(CLASS_NAMES),
                'names': CLASS_NAMES
            }, f)
        
        print(f"[TRAIN] Created dataset config at {config_path}")

    return str(dataset_path)
    
def train_model() -> None:
    """Train YOLO model on generated training data"""

    # Set up project structure
    project_root = Path(".") # Current directory. We'll let things fail if we're not in the right place
    yolo_model, model_type = load_model()
    
    # Update the path attribute in data.yaml to absolute path
    dataset_path = update_dataset_config()
    if dataset_path is None:
        print("[ERROR] Dataset configuration failed. Cannot proceed with training.")
        return
    
    # Generate run name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{model_type}_{timestamp}"

    default_parameter_input = input("[TRAIN] Use default training parameters (Default y)? (y/n): ").strip().lower()
    if default_parameter_input == 'n':
        epochs_input = input("[TRAIN] Enter number of epochs (Default 35): ").strip()
        epochs = int(epochs_input) if epochs_input.isdigit() else 35

        img_size_input = input("[TRAIN] Enter image size (Default 150): ").strip()
        img_size = int(img_size_input) if img_size_input.isdigit() else 160

        batch_size_input = input("[TRAIN] Enter batch size (Default 32): ").strip()
        batch_size = int(batch_size_input) if batch_size_input.isdigit() else 32

        device_input = input("[TRAIN] Enter device (cpu/gpu) (Default gpu): ").strip().lower()
        device = 0 if device_input == 'gpu' and cuda_is_available() else None

        training_config_input = input("[TRAIN] Enter training config file path (Default defaults/train.yaml): ").strip()
        train_config = training_config_input if training_config_input else "defaults/train.yaml"
    else:
        epochs = 35
        img_size = 160
        batch_size = 32
        device = 0 if cuda_is_available() else None  # GPU if available, else CPU
        train_config = "defaults/train.yaml"

    print(f"[TRAIN] Starting training: {run_name}")

    try:
        start_training(yolo_model, dataset_path, epochs, img_size,
                    device, batch_size, project_root, run_name, train_config)
    except Exception as e:
        print(f"[ERROR] Training failed: {e}")
        return
    
    update_input = input("[TRAIN] Update best model? (y/n): ").strip().lower()
    if update_input == 'y':
        best_model_path = project_root / "runs" / run_name / "weights" / "best.pt"
        default_best_model_path = project_root / "defaults" / "best.pt"
        if best_model_path.exists():
            best_model_path.replace(default_best_model_path)
            print(f"[TRAIN] Updated best model at {default_best_model_path}")
        else:
            print(f"[ERROR] Best model not found at {best_model_path}")

def cli_train_model(epochs: int = 35, img_size: int = 160, batch_size: int = 32,
                device: int = 0, train_config: str = "defaults/train.yaml", update_best: bool = True) -> None:
    """
    Train YOLO model on generated training data with CLI parameters
    
    Args:
        epochs: Number of training epochs
        img_size: Image size for training
        batch_size: Batch size for training
        device: Device ID for training
        train_config: Path to training configuration file
        update_best: If True, update the default best model after training
    """

    # Set up project structure
    project_root = Path(".") # Current directory. We'll let things fail if we're not in the right place
    yolo_model, model_type = load_model()
    
    # Update the path attribute in data.yaml to absolute path
    dataset_path = update_dataset_config()
    if dataset_path is None:
        print("[ERROR] Dataset configuration failed. Cannot proceed with training.")
        return
    
    # Generate run name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_name = f"{model_type}_{timestamp}"

    try:
        start_training(yolo_model, dataset_path, epochs, img_size,
                    device, batch_size, project_root, run_name, train_config)
    except Exception as e:
        print(f"[ERROR] Training failed: {e}")
        return
    
    if update_best:
        best_model_path = project_root / "runs" / run_name / "weights" / "best.pt"
        default_best_model_path = project_root / "defaults" / "best.pt"
        if best_model_path.exists():
            best_model_path.replace(default_best_model_path)
        else:
            print(f"[ERROR] Best model not found at {best_model_path}")

def start_training(model: YOLO, dataset: str, epochs: int, img_size: int, 
                device: int, batch_size: int, project_root: Path, 
                run_name: str, train_config: str):
    """
    Trains the YOLO model for classification.
    
    Args:
        model: The YOLO model instance
        dataset: Path to the dataset YAML file
        epochs: Number of training epochs
        img_size: Image size for training
        device: Device ID for training
        batch_size: Batch size for training
        project_root: Root directory for the project
        run_name: Name for this training run
        train_config: Path to training configuration file
        
    Returns:
        Training results
    """
    # Load custom config if provided
    custom_params = {}
    if train_config:
        config_path = project_root / "configs" / train_config
        if config_path.exists():
            with open(config_path, 'r') as f:
                custom_params = yaml.safe_load(f)
            print(f"[TRAIN] Loaded training config from {config_path}")
        else:
            print(f"[WARNING] Config file {config_path} not found, using defaults")
    
    print(f"\n[TRAIN] Training Configuration:")
    print(f"[TRAIN]  Run Name: {run_name}")
    print(f"[TRAIN]  Dataset: {dataset}")
    print(f"[TRAIN]  Epochs: {epochs}")
    print(f"[TRAIN]  Image Size: {img_size}")
    print(f"[TRAIN]  Device: {device}")
    print(f"[TRAIN]  Batch Size: {batch_size}")
    if custom_params:
        print(f"[TRAIN]  Custom Parameters: {list(custom_params.keys())}")
    print()
    
    results = model.train(
        data=dataset,
        epochs=epochs,
        imgsz=img_size,
        device=device,
        batch=batch_size,
        project=str(project_root / "runs"),
        name=run_name,
        exist_ok=False,
        plots=True,
        save=True,
        **custom_params
    )
    
    run_path = project_root / "runs" / "train" / run_name
    print("\n[TRAIN] Training completed!")
    print(f"[TRAIN] Results saved to: {run_path}")
    print(f"[TRAIN] Best weights: {run_path / 'weights' / 'best.pt'}")
    
    return results

def detect_board(image_path_str: str) -> str | None:
    """
    Run YOLO detection on chess board image
    
    Args:
        image_path_str (str): Path to the chess board image

    Returns:
        str | None: Predicted FEN string or None on failure
    """
    try:
        image_path_obj = Path(image_path_str)
        if not image_path_obj.exists():
            print(f"[ERROR] Image file does not exist: {image_path_str}")
            return None

    except Exception as e:
        print(f"[ERROR] Invalid image path: {e}")
        return None

    print(f"\n[DETECT] Running detection on image: {image_path_str}")

    model_path = input("[DETECT] Enter YOLO model path (Default 'defaults/best.pt'): ").strip()
    try:
        if not model_path:
            model_path = Path("defaults/best.pt")
        else:
            model_path = Path(model_path)

        if not model_path.exists():
            print(f"[ERROR] Model file does not exist: {model_path}")
            return None
    except Exception as e:
        print(f"[ERROR] Invalid model path: {e}")
        return None

    image = Image.open(image_path_obj).convert("RGB")
    predictor = ChessPredictor.ChessPiecePredictor(model_path=model_path, device=0, confidence_threshold=0.5)
    predicted_fen, avg_confidence, square_confidences = predictor.predict_board(image, return_confidence=True)
    print(f"[DETECT] Predicted FEN: {predicted_fen}")

    view_choice = input("[DETECT] View prediction confidences? (y/n): ").strip().lower()
    if view_choice == 'y':
        print(f"[DETECT] Average Confidence: {avg_confidence:.4f}")
        print("[DETECT] Square Confidences:")
        for rank in range(8, 0, -1):
            row_confidences = []
            for file in range(1, 9):
                confidence = square_confidences.get(f"{chr(ord('a') + file - 1)}{rank}", 0.0)
                row_confidences.append(f"{confidence:.2f}")
            print(f"[DETECT] {rank} ", " ".join(row_confidences))

    return predicted_fen
