================================================================================
                    SIMPLE 2-STEP INSTALLATION
================================================================================

YOUR GPU: NVIDIA GeForce RTX 2050 (4GB) - DETECTED AND WORKING

ISSUE: Python 3.14 has no GPU support for PyTorch

SOLUTION: 2 simple BAT files

================================================================================
                    STEP 1: INSTALL EVERYTHING
================================================================================

Run this file:

    1_INSTALL_EVERYTHING.bat

What it does:
  • Downloads Python 3.11.9 automatically
  • Installs Python 3.11.9
  • Creates virtual environment in backend\venv
  • Installs GPU-enabled PyTorch with CUDA 12.1
  • Installs all dependencies (ultralytics, flask, etc.)
  • Verifies GPU detection

Time: 10-15 minutes

================================================================================
                    STEP 2: TRAIN MODEL
================================================================================

After Step 1 completes, run:

    2_TRAIN_MODEL.bat

What it does:
  • Activates virtual environment
  • Verifies GPU is working
  • Trains PPE detection model
  • Optimized for RTX 2050 (4GB)
  • Saves model to: backend\runs\detect\ppe_detection\weights\best.pt

Time: 25-40 minutes

Configuration:
  • Model: YOLOv8n (nano - optimized for 4GB)
  • Epochs: 25 (mid-range - optimal)
  • Batch size: 8
  • Image size: 416
  • Quality: GOOD (mAP50: 0.65-0.75)

================================================================================
                    THAT'S IT!
================================================================================

Just 2 files:
  1. 1_INSTALL_EVERYTHING.bat  (run once)
  2. 2_TRAIN_MODEL.bat         (run to train)

Total time: ~40-55 minutes to trained model

================================================================================
                    NOTES
================================================================================

• Python 3.14 will NOT be removed (stays on your system)
• Python 3.11 will be installed alongside
• This project uses Python 3.11 only
• No conflicts between versions
• Everything installs in backend\venv folder

================================================================================
                    REQUIREMENTS
================================================================================

• Internet connection (for downloads)
• ~500MB free disk space
• Windows 10/11

================================================================================
                    TROUBLESHOOTING
================================================================================

If Step 1 fails:
  • Check internet connection
  • Run as Administrator
  • Disable antivirus temporarily

If Step 2 shows "GPU NOT DETECTED":
  • Restart computer
  • Run 1_INSTALL_EVERYTHING.bat again

If training is slow:
  • Close other applications
  • Check GPU usage: nvidia-smi

================================================================================
                    READY TO START?
================================================================================

Run: 1_INSTALL_EVERYTHING.bat

Then: 2_TRAIN_MODEL.bat

Done!

================================================================================
