"""
Auto-Detecting GPU Training Script
Automatically configures based on available hardware
OPTIMIZED: Mid-range epochs for best balance
"""
from ultralytics import YOLO
import torch
import os

def train_ppe_auto():
    print("="*60)
    print("AUTO-DETECTING GPU TRAINING (OPTIMIZED)")
    print("="*60)
    
    # Detect hardware
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\n✓ Device: {device.upper()}")
    
    if device == 'cuda':
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✓ GPU: {gpu_name}")
        print(f"✓ Memory: {gpu_memory:.2f} GB")
        
        # Auto-configure based on GPU memory
        if gpu_memory >= 8:  # 8GB+ GPU (RTX 3060 Ti, RTX 3070, etc.)
            batch_size = 16
            imgsz = 640
            model_size = 's'  # Small model for better accuracy
            epochs = 30  # MID-RANGE: Optimal balance
            print(f"✓ Configuration: HIGH PERFORMANCE (8GB+ GPU)")
        elif gpu_memory >= 6:  # 6GB GPU (RTX 2060, GTX 1660 Ti, etc.)
            batch_size = 12
            imgsz = 640
            model_size = 's'
            epochs = 25  # MID-RANGE
            print(f"✓ Configuration: MEDIUM PERFORMANCE (6GB GPU)")
        else:  # 4GB GPU (GTX 1650, etc.)
            batch_size = 8
            imgsz = 416
            model_size = 'n'  # Nano model for limited memory
            epochs = 25  # MID-RANGE
            print(f"✓ Configuration: OPTIMIZED FOR LIMITED MEMORY")
        
        workers = 4
        device_id = 0
    else:
        print("⚠ CPU mode - Training will be slower")
        batch_size = 8
        imgsz = 416
        model_size = 'n'
        epochs = 25  # MID-RANGE
        workers = 2
        device_id = 'cpu'
    
    print(f"✓ Model: YOLOv8{model_size}")
    print(f"✓ Batch size: {batch_size}")
    print(f"✓ Image size: {imgsz}")
    print(f"✓ Workers: {workers}")
    print(f"✓ Epochs: {epochs}")
    
    # Load appropriate model
    model_file = f'yolov8{model_size}.pt'
    print(f"\n✓ Loading {model_file}...")
    model = YOLO(model_file)
    
    data_path = os.path.abspath('ppe_dataset/data.yaml')
    
    print("\n" + "="*60)
    print("STARTING TRAINING")
    print("="*60)
    print(f"Dataset: {data_path}")
    print(f"\nConfiguration:")
    print(f"  ✓ Model: YOLOv8{model_size}")
    print(f"  ✓ Device: {device.upper()}")
    print(f"  ✓ Epochs: {epochs}")
    print(f"  ✓ Image size: {imgsz}")
    print(f"  ✓ Batch size: {batch_size}")
    print(f"  ✓ Workers: {workers}")
    print(f"  ✓ Mixed precision: Enabled")
    print(f"  ✓ Epochs: {epochs} (MID-RANGE - optimal)")
    
    if device == 'cuda':
        estimated_time = "15-25 minutes" if gpu_memory >= 8 else "20-35 minutes"
    else:
        estimated_time = "1-2 hours"
    
    print(f"\nEstimated time: {estimated_time}")
    print("\nThis provides:")
    print("  ✓ Good accuracy without over-training")
    print("  ✓ Reasonable training time")
    print("  ✓ Production-ready model")
    print("="*60 + "\n")
    
    try:
        results = model.train(
            data=data_path,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch_size,
            name='ppe_detection',
            patience=8,  # Early stopping - optimized
            save=True,
            device=device_id,
            workers=workers,
            plots=True,
            amp=True,  # Mixed precision for faster training
            cache=False,
            verbose=True,
            pretrained=True,
            optimizer='AdamW',
            lr0=0.001,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3,
            warmup_momentum=0.8,
            warmup_bias_lr=0.1,
            box=7.5,
            cls=0.5,
            dfl=1.5,
            hsv_h=0.015,
            hsv_s=0.7,
            hsv_v=0.4,
            degrees=0.0,
            translate=0.1,
            scale=0.5,
            shear=0.0,
            perspective=0.0,
            flipud=0.0,
            fliplr=0.5,
            mosaic=1.0,
            mixup=0.0,
            auto_augment='randaugment',
            erasing=0.4,
            val=True,
            cos_lr=True,
            close_mosaic=5,  # Disable mosaic in last 5 epochs
            exist_ok=False
        )
        
        print("\n" + "="*60)
        print("✓ TRAINING COMPLETE!")
        print("="*60)
        print(f"\n✓ Model saved: runs/detect/ppe_detection/weights/best.pt")
        
        # Validation
        print("\n✓ Validating model...")
        metrics = model.val()
        
        print("\n✓ Model Performance:")
        print(f"  mAP50: {metrics.box.map50:.3f} (detection accuracy)")
        print(f"  mAP50-95: {metrics.box.map:.3f} (overall accuracy)")
        print(f"  Precision: {metrics.box.mp:.3f} (correct detections)")
        print(f"  Recall: {metrics.box.mr:.3f} (found objects)")
        
        # Performance assessment
        if metrics.box.map50 >= 0.7:
            print("\n✓ EXCELLENT MODEL - Ready for production!")
        elif metrics.box.map50 >= 0.5:
            print("\n✓ GOOD MODEL - Suitable for most use cases")
        else:
            print("\n⚠ Model may need more training or data")
        
        print("\n" + "="*60)
        print("MODEL READY FOR USE")
        print("="*60)
        print("\nNext steps:")
        print("  1. Model saved and ready")
        print("  2. Run your application to test")
        print("  3. Check training plots in runs/detect/ppe_detection/")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = train_ppe_auto()
        if success:
            print("\n✓ SUCCESS - Model trained successfully!")
        else:
            print("\n✗ FAILED - Check errors above")
    except KeyboardInterrupt:
        print("\n\n✗ Training interrupted by user")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
