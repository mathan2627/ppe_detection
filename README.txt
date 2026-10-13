========================================
PPE DETECTION SYSTEM
========================================

QUICK START:
------------

1. Install Dependencies:
   fix_torchvision.bat

2. Train Model (Choose one):
   - train_proper.bat (30-60 min, high quality)
   - train_fresh.bat (5-10 min, quick test)

3. Start System:
   start_venv.bat

4. Open Browser:
   http://localhost:3000

REQUIREMENTS:
-------------
- Python 3.8+
- Node.js 16+
- NVIDIA GPU (optional)
- MongoDB (optional)

DATASET:
--------
Place your PPE dataset in:
backend/ppe_dataset/

Structure:
  ├── data.yaml
  ├── train/images/ and train/labels/
  ├── valid/images/ and valid/labels/
  └── test/images/ and test/labels/

FILES:
------
Essential BAT files:
- fix_torchvision.bat - Setup
- train_proper.bat - Train (recommended)
- train_fresh.bat - Quick train
- start_venv.bat - Start system
- install.bat - Install only

Backend:
- backend/app.py - Main API
- backend/train_ppe_proper.py - Proper training
- backend/train_ppe_fast.py - Fast training

Frontend:
- frontend/pages/index.tsx - Main UI
- frontend/pages/analytics.tsx - Analytics

FEATURES:
---------
✓ PPE Detection (Helmet, Vest, Gloves, Mask, Goggles)
✓ Normal Detection (80 objects)
✓ Real-time camera detection
✓ Analytics with CSV/PDF export
✓ MongoDB integration

LICENSE:
--------
MIT

========================================
