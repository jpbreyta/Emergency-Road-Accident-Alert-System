





https://github.com/user-attachments/assets/69ecddbf-3db9-43bb-9c0e-81497fb50600






# Road Accident Detection & Alert System

## Prerequisites

Before starting, ensure you have the following installed on your system:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **pip** (Python package manager - usually comes with Python)

## Installation Guide

### 1. Clone the Repository

Open a terminal (Command Prompt, PowerShell, or Terminal) and run:

```bash
git clone https://github.com/jared27906/SJRoad.git
cd SJRoad
```

### 2. Create Python Virtual Environment

> [!NOTE]
> A virtual environment keeps project dependencies isolated. You should see `(venv)` appear in your terminal when activated.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Packages

> [!IMPORTANT]
> This step installs all necessary Python libraries. It may take several minutes.

```bash
pip install --upgrade pip
pip install -r imports.txt
```

**Packages that will be installed:**
- `tensorflow` - Machine learning framework
- `keras` - Deep learning API
- `opencv-python` - Computer vision library
- `numpy` - Numerical computing
- `pandas` - Data manipulation
- `matplotlib` - Visualization
- `Pillow` - Image processing
- `twilio` - SMS/Call alerts
- `flask` - Web framework (if using web interface)

### 4. Download Model Weights

Download the pre-trained model file:

📥 [Download model_weights.h5](https://www.mediafire.com/file/hdwt1onaba581uq/model_weights.h5/file)

Place the downloaded `model_weights.h5` file in the root directory of the project (same folder as `main.py`).

### 5. Configure Environment Variables (.env)

Create or edit the `.env` file in the project root with your configuration:

```bash
# Twilio Configuration (for emergency alerts)
TWILIO_ACCOUNT_SID=your_account_sid_here
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_FROM_NUMBER=your_twilio_phone_number
EMERGENCY_NUMBER=emergency_contact_number
TWILIO_ENABLED=True
AUTO_CALL=False

# Detection Settings
CONFIDENCE_THRESHOLD=95
MIN_DETECTION_FRAMES=5
WARMUP_FRAMES=300

# Model Files
MODEL_JSON=model.json
MODEL_WEIGHTS=model_weights.h5

# Video Source (change as needed)
VIDEO_SOURCE=test_video.mp4

# Web Interface Settings
WEB_HOST=0.0.0.0
WEB_PORT=5000
WEB_DEBUG=False

# Photo Storage
PHOTO_DIRECTORY=accident_photos
```

**To get Twilio credentials:**
1. Sign up for a free account at [Twilio](https://www.twilio.com/try-twilio)
2. Get your Account SID and Auth Token from the Twilio Console
3. Get a Twilio phone number (free trial includes one)
4. Replace the placeholder values in `.env`

> [!TIP]
> Set `TWILIO_ENABLED=False` if you want to test without making actual calls.

### 6. Configure Camera Source (Optional)

If using an RTSP camera instead of the test video:

Edit the `.env` file and change the `VIDEO_SOURCE` line:

```bash
VIDEO_SOURCE=rtsp://username:password@camera_ip:554/live/ch00_0
```

**Example:**
```bash
VIDEO_SOURCE=rtsp://admin:password123@192.168.1.100:554/live/ch00_0
```

### 7. Run the Application

**Option A: Command-line interface**
```bash
python main.py
```

**Option B: Web interface**
```bash
python web_app.py
```

Then open your browser and go to: `http://localhost:5000`

## Troubleshooting

**Issue: "python not found"**
- Try using `python3` instead of `python`
- Ensure Python is added to your system PATH

**Issue: "No module named 'tensorflow'"**
- Make sure your virtual environment is activated (you should see `(venv)` in terminal)
- Run `pip install -r imports.txt` again

**Issue: "Failed to open video source"**
- Check that `test_video.mp4` exists in the project folder
- Verify your camera URL if using RTSP
- Ensure your camera is accessible on the network

**Issue: Twilio errors**
- Verify your credentials in `.env` are correct
- Set `TWILIO_ENABLED=False` to disable calls during testing

