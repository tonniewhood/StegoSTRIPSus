import argparse
import json
import yaml
from datetime import datetime
from pathlib import Path
from ultralytics import YOLO

def main() -> None:
    """Main entry point for training, tuning, or comparing YOLO models."""
    args = parse_arguments()
    
    # Set up project structure
    project_root = Path(args.project_root)
    if args.make_configs:
        create_example_configs(project_root / "configs")
    
    # Initialize new model from models directory or ultralytics hub
    model_path = project_root / "models" / args.model_type
    if model_path.exists():
        model = YOLO(str(model_path))
        print(f"Loaded model from local: {model_path}")
    else:
        # Will download from ultralytics
        model = YOLO(args.model_type)
        print(f"Initialized model: {args.model_type} (downloaded from ultralytics)")
    
    # Create dataset config if it doesn't exist
    dataset_path = Path(args.dataset)
    if not (dataset_path / "data.yaml").exists():
        print(f"`data.yaml` not found in {dataset_path}. Exiting.")
        return
    
    # Update the path attribute in data.yaml to absolute path and save to a temp file
    temp_data_yaml = update_dataset_config(dataset_path, args.project_root)
    
    # Generate run name
    run_name = generate_run_name(args)
    print(f"Starting training: {run_name}")
    train_model(model, str(dataset_path), args.epochs, args.img_size,
                args.device, args.batch_size, project_root, run_name, args.train_config)
    
    # Clean up temporary data.yaml
    if temp_data_yaml.exists():
        temp_data_yaml.unlink()

def create_example_configs(config_dir: Path) -> None:
    """Creates example configuration files if they don't exist."""
    
    # Example training config
    train_config_path = config_dir / "example_train.yaml"
    if not train_config_path.exists():
        train_config = {
            "optimizer": "AdamW",
            "lr0": 0.001,
            "momentum": 0.9,
            "weight_decay": 0.0005,
            "warmup_epochs": 3,
            "patience": 50,
            "save_period": 10,
            "dropout": 0.2,
            "label_smoothing": 0.1,
            "hsv_h": 0.015,
            "hsv_s": 0.7,
            "hsv_v": 0.4,
            "degrees": 5.0,
            "translate": 0.1,
            "scale": 0.5,
            "flipud": 0.0,
            "fliplr": 0.5,
            "mosaic": 1.0,
            "mixup": 0.0
        }
        with open(train_config_path, 'w') as f:
            yaml.dump(train_config, f, default_flow_style=False, sort_keys=False)
        print(f"Created example training config: {train_config_path}")

def generate_run_name(args) -> str:
    """Generate a descriptive run name based on arguments."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    model_name = Path(args.model_type).stem
    
    if args.run_name:
        return f"{args.run_name}_{timestamp}"
    else:
        return f"{model_name}_{timestamp}"

def save_run_metadata(run_path: Path, args, results) -> None:
    """Save metadata about the training run."""
    metadata = {
        "timestamp": datetime.now().isoformat(),
        "model_type": args.model_type,
        "dataset": args.dataset,
        "epochs": args.epochs,
        "img_size": args.img_size,
        "batch_size": args.batch_size,
        "device": args.device,
        "config_file": args.train_config,
        "results_summary": {
            "final_metrics": str(results) if results else "N/A"
        }
    }
    
    metadata_path = run_path / "metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Saved run metadata to {metadata_path}")

def update_dataset_config(dataset_path: Path, project_root: str) -> Path:
    """
    Creates a YAML configuration file for the dataset if it doesn't exist.
    
    Args:
        dataset_path: Path to the dataset directory

    Returns:
        Path to the temporary data.yaml file created.
    """
    config_path = dataset_path / "data.yaml"
    temp_config_path = Path(project_root) / "temp_data.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"`data.yaml` not found in {dataset_path}. Please create it before proceeding.")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

        # Update paths to absolute paths
        config['path'] = str(dataset_path.absolute())
        config['train'] = str((dataset_path / "train").absolute())
        config['val'] = str((dataset_path / "val").absolute())

        print(f"Created temporary dataset config at {temp_config_path}")
        print(f"Dataset paths updated to: {config['path']}")
        print(f"Training images path: {config['train']}")
        print(f"Validation images path: {config['val']}")

    with open(temp_config_path, 'w') as f:
        yaml.safe_dump(config, f)

    return temp_config_path



def train_model(model: YOLO, dataset: str, epochs: int, img_size: int, 
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
            print(f"Loaded training config from {config_path}")
        else:
            print(f"Warning: Config file {config_path} not found, using defaults")
    
    print(f"\nTraining Configuration:")
    print(f"  Run Name: {run_name}")
    print(f"  Dataset: {dataset}")
    print(f"  Epochs: {epochs}")
    print(f"  Image Size: {img_size}")
    print(f"  Device: {device}")
    print(f"  Batch Size: {batch_size}")
    if custom_params:
        print(f"  Custom Parameters: {list(custom_params.keys())}")
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
    
    # Save metadata
    run_path = project_root / "runs" / run_name
    save_run_metadata(run_path, argparse.Namespace(
        model_type=model.model_name if hasattr(model, 'model_name') else 'unknown',
        dataset=dataset,
        epochs=epochs,
        img_size=img_size,
        batch_size=batch_size,
        device=device,
        train=True,
        tune=False,
        train_config=train_config,
        tune_config=None
    ), results)
    
    print("\nTraining completed!")
    print(f"Results saved to: {run_path}")
    print(f"Best weights: {run_path / 'weights' / 'best.pt'}")
    
    return results

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Train a YOLO classification model for chess pieces.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Mode selection
    parser.add_argument("--train", action="store_true", 
                       help="Train a new model")
    
    # Project structure
    parser.add_argument("--project-root", type=str, default=".",
                       help="Root directory for models, configs, and runs")
    parser.add_argument("--run-name", type=str, default="",
                       help="Custom name for this run (timestamp will be appended)")
    
    # Model configuration
    parser.add_argument("--model-type", type=str, default="yolov8n-cls.pt",
                       help="YOLO model (e.g., yolov8n-cls.pt, yolov8s-cls.pt, yolov8m-cls.pt)")
    parser.add_argument("--make-configs", action="store_true",
                       help="Create example configuration files in the configs/ directory")
    
    # Dataset configuration
    parser.add_argument("--dataset", type=str, default="datasets/chess_pieces",
                       help="Path to the dataset directory")
    
    # Training parameters
    parser.add_argument("--epochs", type=int, default=35,
                       help="Number of training epochs")
    parser.add_argument("--img-size", type=int, default=150,
                       help="Image size for training")
    parser.add_argument("--device", type=int, default=0,
                       help="Device ID (0 for GPU, -1 for CPU)")
    parser.add_argument("--batch-size", type=int, default=32,
                       help="Batch size for training")
    
    # Configuration files
    parser.add_argument("--train-config", type=str, default="",
                       help="Training config filename (in configs/)")
    
    return parser.parse_args()

if __name__ == "__main__":
    main()