"""
ULTRA-FAST YOLOv8 Training - Completes in 3-5 minutes
Optimized for speed while maintaining decent accuracy
"""
from ultralytics import YOLO
import torch

def train_ppe_fast():
    print("="*60)
    print("ULTRA-FAST YOLOv8 Training (3-5 minutes)")
    print("="*60)
    
    # Check GPU with detailed info
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
        print("1. Run: install_gpu_dependencies.bat")
        print("2. Restart this script")
        print("="*60)
        input("\nPress Enter to continue with CPU training (slow) or Ctrl+C to exit...")
    
    if device == 'cuda':
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✓ GPU: {gpu_name}")
        print(f"✓ Memory: {gpu_memory:.2f} GB")
        
        # Optimized for RTX 3060 Ti (8GB) - Use GPU fully
        batch_size = 32
        workers = 4
        imgsz = 416
    else:
        print("⚠ CPU mode - will take longer")
        batch_size = 8
        workers = 2
        imgsz = 416
    
    print(f"✓ Batch size: {batch_size}")
    print(f"✓ Image size: {imgsz}")
    print(f"✓ Workers: {workers} (reduced to avoid memory errors)")
    print(f"✓ Epochs: 10 (REDUCED for speed)")
    
    # Load smallest YOLOv8 model
    print("\n✓ Loading YOLOv8n (nano - fastest)...")
    model = YOLO('yolov8n.pt')
    
    # Ultra-fast training configuration
    import os
    data_path = os.path.abspath('ppe_dataset/data.yaml')
    
    print("\n" + "="*60)
    print("STARTING FAST TRAINING")
    print("="*60)
    print("Dataset:", data_path)
    print("Settings:")
    print("  ✓ Epochs: 10 (fast training)")
    print("  ✓ Image size: 416 (optimized)")
    print("  ✓ Batch size: " + str(batch_size))
    print("  ✓ Workers: " + str(workers) + " (GPU optimized)")
    print("  ✓ Mixed precision: Enabled")
    print("\nEstimated time: 5-10 minutes on GPU")
    print("="*60 + "\n")
    
    try:
        results = model.train(
            data=data_path,
            epochs=10,
            imgsz=imgsz,
            batch=batch_size,
            name='ppe_detection',
            patience=0,
            save=True,
            device=0 if device == 'cuda' else 'cpu',
            workers=workers,
            plots=True,
            amp=True,
            cache=False,
            verbose=True,
            pretrained=True,
            optimizer='SGD',
            lr0=0.01,
            momentum=0.9,
            weight_decay=0.0005,
            warmup_epochs=1,
            close_mosaic=0,
            rect=True,
            single_cls=False,
            cos_lr=False,
            label_smoothing=0.0,
            val=True,
            save_period=-1
        )
        
        print("\n" + "="*60)
        print("✓ TRAINING COMPLETE!")
        print("="*60)
        print(f"\n✓ Model saved: runs/detect/ppe_detection/weights/best.pt")
        print(f"✓ Ready to use with app.py")
        
        # Quick validation
        print("\n✓ Validating model...")
        metrics = model.val()
        
        print("\n✓ Model Performance:")
        print(f"  mAP50: {metrics.box.map50:.3f}")
        print(f"  mAP50-95: {metrics.box.map:.3f}")
        
        print("\n" + "="*60)
        print("MODEL READY - Run start.bat to launch system")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    try:
        success = train_ppe_fast()
        if success:
            print("\n✓ SUCCESS - Model trained in record time!")
        else:
            print("\n✗ FAILED - Check errors above")
    except KeyboardInterrupt:
        print("\n\n✗ Training interrupted by user")
    except Exception as e:
        print(f"\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
