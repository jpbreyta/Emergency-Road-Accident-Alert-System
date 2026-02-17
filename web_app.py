from flask import Flask, render_template, Response, jsonify
import cv2
import numpy as np
import time
import os
from detection import AccidentDetectionModel
from twilio.rest import Client
from utils import setup_gpu, preprocess_frame, save_accident_photo
from config import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, 
    EMERGENCY_NUMBER, TWILIO_ENABLED, AUTO_CALL,
    CONFIDENCE_THRESHOLD, WARMUP_FRAMES, MIN_DETECTION_FRAMES,
    VIDEO_SOURCE, MODEL_JSON, MODEL_WEIGHTS, WEB_HOST, WEB_PORT, WEB_DEBUG
)

app = Flask(__name__)

# ===================== GPU SETUP =====================
setup_gpu()

# ===================== MODEL =====================
model = AccidentDetectionModel(MODEL_JSON, MODEL_WEIGHTS)

# ===================== GLOBAL STATE =====================
accident_detected = False
last_detection_time = None
detection_confidence = 0
total_accidents = 0
call_made = False

def call_ambulance():
    global call_made
    
    if not TWILIO_ENABLED:
        print("⚠️ Twilio calls disabled")
        call_made = True
        return True
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            url="http://demo.twilio.com/docs/voice.xml",
            to=EMERGENCY_NUMBER,
            from_=TWILIO_FROM_NUMBER
        )
        call_made = True
        print(f"📞 Emergency call made! SID: {call.sid}")
        return True
    except Exception as e:
        print(f"⚠️ Twilio error: {e}")
        print("💡 Tip: Set TWILIO_ENABLED = False to disable calls for testing")
        # Still mark as "called" for demo purposes
        call_made = True
        return False

# Preprocessing and photo saving functions imported from utils.py

def generate_frames():
    global accident_detected, last_detection_time, detection_confidence, total_accidents, call_made
    
    # Open video source with proper settings
    if isinstance(VIDEO_SOURCE, int):
        # Webcam
        cap = cv2.VideoCapture(VIDEO_SOURCE)
        print(f"📷 Opening webcam {VIDEO_SOURCE}...")
    elif VIDEO_SOURCE.startswith("rtsp"):
        # RTSP/CCTV stream
        os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp|timeout;60000000'
        cap = cv2.VideoCapture(f"{VIDEO_SOURCE}?rtsp_transport=tcp", cv2.CAP_FFMPEG)
        cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 60000)
        cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 60000)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        print(f"📡 Connecting to RTSP stream...")
    else:
        # Video file
        cap = cv2.VideoCapture(VIDEO_SOURCE)
        print(f"🎬 Opening video file: {VIDEO_SOURCE}")
    
    if not cap.isOpened():
        print(f"❌ Failed to open video source: {VIDEO_SOURCE}")
        return
    
    frame_id = 0
    font = cv2.FONT_HERSHEY_SIMPLEX
    consecutive_accident_frames = 0  # Track consecutive accident detections
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            # Loop video file, reconnect for streams
            if isinstance(VIDEO_SOURCE, str) and not VIDEO_SOURCE.startswith("rtsp"):
                # Video file - loop it
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            else:
                # Stream or webcam - wait and retry
                time.sleep(0.1)
            continue
        
        frame_id += 1
        
        # Process every 2nd frame for performance
        if frame_id % 2 == 0:
            roi = preprocess_frame(frame)
            pred, prob = model.predict_accident(roi[np.newaxis, ...])
            
            # Model returns probabilities for [Accident, No Accident]
            accident_prob = round(prob[0][0] * 100, 2)
            no_accident_prob = round(prob[0][1] * 100, 2)
            
            # Debug: Print every 60 frames
            if frame_id % 60 == 0:
                print(f"Frame {frame_id}: {pred} | Accident:{accident_prob}% | NoAccident:{no_accident_prob}%")
            
            # Use accident probability for detection
            detection_confidence = accident_prob
            
            # Skip warmup period
            if frame_id < WARMUP_FRAMES:
                cv2.rectangle(frame, (10, 10), (300, 60), (255, 165, 0), -1)
                cv2.putText(frame, f"Warming up... {frame_id}/{WARMUP_FRAMES}", 
                           (20, 45), font, 0.6, (255, 255, 255), 2)
            elif pred == "Accident" and accident_prob > CONFIDENCE_THRESHOLD:
                consecutive_accident_frames += 1
                
                # Draw red box
                cv2.rectangle(frame, (10, 10), (400, 60), (0, 0, 255), -1)
                cv2.putText(frame, f"ACCIDENT! {accident_prob}% ({consecutive_accident_frames}/{MIN_DETECTION_FRAMES})", 
                           (20, 45), font, 0.6, (255, 255, 255), 2)
                
                # Trigger alert only after consecutive detections
                if consecutive_accident_frames >= MIN_DETECTION_FRAMES and not accident_detected:
                    accident_detected = True
                    from datetime import datetime
                    last_detection_time = datetime.now().strftime("%B %d, %Y at %I:%M:%S %p")
                    total_accidents += 1
                    print(f"🚨 ACCIDENT LOGGED! Total: {total_accidents}, Time: {last_detection_time}, Confidence: {accident_prob}%")
                    save_accident_photo(frame)
                    if AUTO_CALL:
                        call_ambulance()
                        print("📞 Auto-calling ambulance...")
                    else:
                        print("⚠️ Accident detected! Use 'Call Ambulance' button to call.")
            else:
                # Reset consecutive counter
                consecutive_accident_frames = 0
                
                # Normal traffic
                cv2.rectangle(frame, (10, 10), (300, 60), (0, 255, 0), -1)
                cv2.putText(frame, f"Normal {no_accident_prob}%", 
                           (20, 45), font, 0.7, (0, 0, 0), 2)
        
        # Encode frame
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.03)  # ~30 FPS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    global accident_detected, last_detection_time, detection_confidence, total_accidents, call_made
    return jsonify({
        'accident_detected': accident_detected,
        'last_detection_time': last_detection_time,
        'confidence': float(detection_confidence),  # Convert to Python float
        'total_accidents': int(total_accidents),  # Convert to Python int
        'call_made': call_made,
        'emergency_number': EMERGENCY_NUMBER
    })

@app.route('/reset_alert')
def reset_alert():
    global accident_detected, call_made
    accident_detected = False
    call_made = False
    return jsonify({'status': 'ok'})

@app.route('/manual_call')
def manual_call():
    success = call_ambulance()
    return jsonify({'status': 'success' if success else 'failed'})

if __name__ == '__main__':
    print("🌐 Starting web interface...")
    print(f"📱 Open browser: http://localhost:{WEB_PORT}")
    app.run(debug=WEB_DEBUG, host=WEB_HOST, port=WEB_PORT, threaded=True)
