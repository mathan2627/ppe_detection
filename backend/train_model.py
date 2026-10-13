"""
Simple Training Script for PPE Detection
Optimized for RTX 2050 (4GB)
"""
from ultralytics import YOLO
import torch
import os

print('='*70)
print('TRAINING CONFIGURATION')
print('='*70)

# Check device
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f'Device: {device.upper()}')

if device == 'cuda':
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'Memory: {torch.cuda.get_device_properties(0).total_memory/1024**3:.2f} GB')

print('Model: YOLOv8n (nano)')
print('Epochs: 25')
print('Batch size: 8')
print('Image size: 416')
print('Workers: 2')
print('='*70)
print()

# Load model
print('Loading YOLOv8n model...')
model = YOLO('yolov8n.pt')

# Get data path
data_path = os.path.abspath('ppe_dataset/data.yaml')
print(f'Dataset: {data_path}')
print()

print('Starting training...')
print('This will take 25-40 minutes on RTX 2050')
print()

# Train model
results = model.train(
    data=data_path,
    epochs=25,
    imgsz=416,
    batch=8,
    name='ppe_detection',
    patience=8,
    save=True,
    device=0 if device=='cuda' else 'cpu',
    workers=2,
    plots=True,
    amp=True,
    cache=False,
    verbose=True,
    pretrained=True,
    optimizer='AdamW',
    lr0=0.001,
    lrf=0.01,
    momentum=0.937,
    weight_decay=0.0005,
    warmup_epochs=3,
    val=True,
    cos_lr=True,
    exist_ok=False
)

print()
print('='*70)
print('TRAINING COMPLETE!')
print('='*70)
print()

# Validate model
print('Validating model...')
metrics = model.val()

print()
print('Model Performance:')
print(f'  mAP50: {metrics.box.map50:.3f}')
print(f'  mAP50-95: {metrics.box.map:.3f}')
print(f'  Precision: {metrics.box.mp:.3f}')
print(f'  Recall: {metrics.box.mr:.3f}')
print()

if metrics.box.map50 >= 0.65:
    print('STATUS: EXCELLENT MODEL - Ready for production!')
elif metrics.box.map50 >= 0.50:
    print('STATUS: GOOD MODEL - Suitable for use')
else:
    print('STATUS: Model may need more training')

print()
print('='*70)
print('Model saved to: runs/detect/ppe_detection/weights/best.pt')
print('='*70)
