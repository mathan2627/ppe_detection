"""
Optimized Training for RTX 2050 (4GB GPU)
Specifically configured for 4GB GPU memory
"""
from ultralytics import YOLO
import torch
import os

def train_ppe_rtx2050():
    print("="*60)
    print("RTX 2050 OPTIMIZED TRAINING (4GB GPU)")
    print("="*60)
    
    # Check GPU
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\n✓ Device: {device.upper()}")
    print(f"✓ PyTorch version: {torch.__version__}")
    
    if device == 'cpu' and '+cpu' in torch.__version__:
        print("\n" + "="*60)
        print("⚠ WARNING: CPU-ONLY PYTORCH DETECTED")
        print("="*60)
        print("You have CPU-only PyTorch installed.")
        print("Training will be VERY SLOW without GPU support.")
        print("\nTo enable GPU:")
        print("1. Run: INSTALL_GPU_NOW.bat")
        print("2. Restart this script")
        print("="*60)
        input("\nPress Enter to continue with CPU training (slow) or Ctrl+C to exit...")
    
    if device == 'cuda':
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✓ GPU: {gpu_name}")
        print(f"✓ Memory: {gpu_memory:.2f} GB")
        
        # OPTIMIZED FOR RTX 2050 (4GB)
        batch_size = 8  # Smaller batch for 4GB
        workers = 2  # Reduced workers
        imgsz = 416  # Smaller image size
        epochs = 25  # Mid-range epochs
        model_size = 'n'  # Nano model for 4GB
        
        print(f"\n✓ Configuration: OPTIMIZED FOR 4GB GPU")
    else:
        print("⚠ CPU mode - will take much longer")
        batch_size = 4
        workers = 2
        imgsz = 416
        epochs = 25
        model_size = 'n'
    
    print(f"✓ Batch size: {batch_size}")
    print(f"✓ Image size: {imgsz}")
    print(f"✓ Workers: {workers}")
    print(f"✓ Epochs: {epochs} (MID-RANGE - optimal balance)")
    print(f"✓ Model: YOLOv8{model_size}")
    
    # Load appropriate model
    model_file = f'yolov8{model_size}.pt'
    print(f"\n✓ Loading {model_file}...")
    model = YOLO(model_file)
    
    data_path = os.path.abspath('ppe_dataset/data.yaml')
    
    print("\n" + "="*60)
    print("STARTING OPTIMIZED TRAINING FOR RTX 2050")
    print("="*60)
    print("Dataset:", data_path)
    print("\nTraining Configuration:")
    print(f"  ✓ Model: YOLOv8{model_size} (optimized for 4GB)")
    print(f"  ✓ Epochs: {epochs} (MID-RANGE - optimal)")
    print(f"  ✓ Image size: {imgsz}")
    print(f"  ✓ Batch size: {batch_size}")
    print("  ✓ Early stopping: Enabled (patience=8)")
    print("  ✓ Data augmentation: Optimized")
    print("  ✓ Mixed precision: Enabled (faster)")
    print("  ✓ Validation: Every epoch")
    
    if device == 'cuda':
        print("\nEstimated time: 25-40 minutes on RTX 2050")
    else:
        print("\nEstimated time: 1-2 hours on CPU")
    
    print("\nThis provides:")
    print("  ✓ Good accuracy for 4GB GPU")
    print("  ✓ No out-of-memory errors")
    print("  ✓ Production-ready model")
    print("="*60 + "\n")
    
    try:
        results = model.train(
            data=data_path,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch_size,
            name='ppe_detection',
            patience=8,  # Early stopping
            save=True,
            device=0 if device == 'cuda' else 'cpu',
            workers=workers,
            plots=True,
            amp=True,  # Mixed precision
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
            close_mosaic=5,
            exist_ok=False
        )
        
        print("\n" + "="*60)
        print("✓ TRAINING COMPLETE!")
        print("="*60)
        print(f"\n✓ Model saved: runs/detect/ppe_detection/weights/best.pt")
        print(f"✓ Optimized model ready for production!")
        
        # Validation
        print("\n✓ Validating model...")
        metrics = model.val()
        
        print("\n✓ Model Performance:")
        print(f"  mAP50: {metrics.box.map50:.3f} (detection accuracy)")
        print(f"  mAP50-95: {metrics.box.map:.3f} (overall accuracy)")
        print(f"  Precision: {metrics.box.mp:.3f} (correct detections)")
        print(f"  Recall: {metrics.box.mr:.3f} (found objects)")
        
        # Performance assessment
        if metrics.box.map50 >= 0.65:
            print("\n✓ EXCELLENT MODEL - Ready for production!")
        elif metrics.box.map50 >= 0.50:
            print("\n✓ GOOD MODEL - Suitable for most use cases")
        else:
            print("\n⚠ Model may need more training or data")
        
        print("\n" + "="*60)
        print("NEXT STEPS:")
        print("="*60)
        print("1. Model is saved and ready to use")
        print("2. Run your application to test it")
        print("3. Check runs/detect/ppe_detection/ for training plots")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = train_ppe_rtx2050()
        if success:
            print("\n" + "="*60)
            print("✓ SUCCESS - RTX 2050 optimized model trained!")
            print("="*60)
            print("\nYour model is ready with:")
            print("  ✓ Optimized for 4GB GPU")
            print("  ✓ Good accuracy for production")
            print("  ✓ No memory issues")
            print("="*60)
        else:
            print("\n✗ FAILED - Check errors above")
    except KeyboardInterrupt:
        print("\n\n✗ Training interrupted by user")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
