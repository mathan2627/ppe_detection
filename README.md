# PPE Detection System

AI-powered PPE detection with YOLOv8, Flask, Next.js, and MongoDB.

## Quick Start

### 1. Install Dependencies
```bash
fix_torchvision.bat
```
This creates virtual environment and installs everything (GPU PyTorch + all dependencies).

### 2. Train Model
```bash
train_fresh.bat
```
Trains PPE detection model using GPU (5-10 minutes).

### 3. Start System
```bash
start_venv.bat
```
Launches backend and frontend.

Open: http://localhost:3000

## Files

**Essential BAT files:**
- `fix_torchvision.bat` - Setup (one time)
- `train_fresh.bat` - Train model
- `start_venv.bat` - Start system
- `start.bat` - Alternative start (system Python)
- `install.bat` - Install dependencies only

**Backend:**
- `backend/app.py` - Main Flask API
- `backend/train_ppe_fast.py` - Training script
- `backend/requirements.txt` - Python dependencies

**Frontend:**
- `frontend/pages/index.tsx` - Main UI
- `frontend/pages/analytics.tsx` - Analytics page

## Features

- PPE Detection: Helmet, Vest, Boots, Shoes, Mask, Gloves, Goggles, Glasses, Apron
- Normal Detection: 80 common objects
- Real-time detection
- Analytics with CSV/PDF export
- MongoDB integration

## Requirements

- Python 3.8+
- Node.js 16+
- NVIDIA GPU (optional, for faster training)
- MongoDB (optional, for analytics)

## License

MIT
