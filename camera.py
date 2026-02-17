import cv2
import numpy as np
import os
import threading
import time
import tkinter as tk
from twilio.rest import Client
from PIL import Image, ImageTk
from detection import AccidentDetectionModel
from utils import setup_gpu, preprocess_frame, save_accident_photo
from config import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER,
    EMERGENCY_NUMBER, VIDEO_SOURCE, MODEL_JSON, MODEL_WEIGHTS,
    CONFIDENCE_THRESHOLD
)

# ===================== GPU SETUP =====================
setup_gpu()

# ===================== MODEL =====================
model = AccidentDetectionModel(MODEL_JSON, MODEL_WEIGHTS)

font = cv2.FONT_HERSHEY_SIMPLEX
alarm_triggered = False

# ===================== RTSP THREAD =====================
class RTSPCamera:
    def __init__(self, url):
        self.url = url
        
        # Check if it's a webcam (integer) or stream/file (string)
        if isinstance(url, int):
            # Webcam
            self.cap = cv2.VideoCapture(url)
            print(f"📷 Opening webcam {url}...")
        else:
            # RTSP stream or video file
            if url.startswith("rtsp"):
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp|timeout;60000000'
                self.cap = cv2.VideoCapture(f"{url}?rtsp_transport=tcp", cv2.CAP_FFMPEG)
                self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 60000)
                self.cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 60000)
            else:
                # Video file
                self.cap = cv2.VideoCapture(url)
        
        # Check if video opened successfully
        if not self.cap.isOpened():
            raise Exception(f"Failed to open video source: {url}")
        
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

        self.frame = None
        self.running = True
        self.lock = threading.Lock()

        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        reconnect_attempts = 0
        max_reconnect_attempts = 5
        
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.frame = frame
                reconnect_attempts = 0  # Reset on successful read
                time.sleep(0.03)  # ~30 FPS
            else:
                # Check if it's a video file that ended
                if isinstance(self.url, str) and not self.url.startswith("rtsp"):
                    # Video file ended, loop it
                    print("🔄 Video ended, restarting...")
                    self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    reconnect_attempts = 0
                    time.sleep(1)  # Wait before restarting
                    continue
                
                print(f"⚠️ Failed to read frame. Attempt {reconnect_attempts + 1}/{max_reconnect_attempts}")
                reconnect_attempts += 1
                
                if reconnect_attempts >= max_reconnect_attempts:
                    print("🔄 Attempting to reconnect...")
                    self.cap.release()
                    time.sleep(2)
                    
                    # Reconnect based on source type
                    if isinstance(self.url, int):
                        self.cap = cv2.VideoCapture(self.url)
                    else:
                        if self.url.startswith("rtsp"):
                            os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'rtsp_transport;tcp|timeout;60000000'
                            self.cap = cv2.VideoCapture(f"{self.url}?rtsp_transport=tcp", cv2.CAP_FFMPEG)
                            self.cap.set(cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 60000)
                            self.cap.set(cv2.CAP_PROP_READ_TIMEOUT_MSEC, 60000)
                        else:
                            self.cap = cv2.VideoCapture(self.url)
                    
                    self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                    reconnect_attempts = 0
                else:
                    time.sleep(0.5)

    def read(self):
        with self.lock:
            return self.frame

    def stop(self):
        self.running = False
        self.cap.release()

# ===================== FRAME SKIP CONTROL =====================
class DynamicSkipper:
    def __init__(self):
        self.skip = 1

    def update(self, inference_ms):
        if inference_ms > 80:
            self.skip = min(self.skip + 1, 10)
        else:
            self.skip = max(self.skip - 1, 1)

# Preprocessing and photo saving functions imported from utils.py

def call_ambulance():
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            url="http://demo.twilio.com/docs/voice.xml",
            to=EMERGENCY_NUMBER,
            from_=TWILIO_FROM_NUMBER
        )
        print("📞 Ambulance Call SID:", call.sid)
    except Exception as e:
        print("Twilio error:", e)

# ===================== ALERT UI =====================
def show_alert_message():
    def on_call():
        call_ambulance()
        alert.destroy()

    alert = tk.Tk()
    alert.title("Accident Alert")
    alert.geometry("500x250")

    tk.Label(
        alert,
        text="🚨 Accident Detected!\nIs it critical?",
        font=("Helvetica", 16)
    ).pack()

    try:
        gif = Image.open("alert.gif").resize((150, 100))
        global gif_image
        gif_image = ImageTk.PhotoImage(gif)
        tk.Label(alert, image=gif_image).pack()
    except:
        pass

    tk.Button(alert, text="Call Ambulance", command=on_call).pack()
    tk.Button(alert, text="Cancel", command=alert.destroy).pack()

    alert.mainloop()

def start_alert_thread():
    threading.Thread(target=show_alert_message, daemon=True).start()

# ===================== MAIN LOOP =====================
def startapplication():
    # Use configured video source from config.py
    cam = VIDEO_SOURCE
    global alarm_triggered

    camera = RTSPCamera(cam)
    print(f"✅ Connected to video source: {cam}")
    
    skipper = DynamicSkipper()
    frame_id = 0

    while True:
        frame = camera.read()
        if frame is None:
            time.sleep(0.1)  # Wait a bit before checking again
            continue

        frame_id += 1
        display = cv2.resize(frame, (250, 250))

        if frame_id % skipper.skip == 0:
            start = time.time()

            roi = preprocess_frame(frame)
            pred, prob = model.predict_accident(roi[np.newaxis, ...])

            infer_ms = (time.time() - start) * 1000
            skipper.update(infer_ms)

            confidence = round(prob[0][0] * 100, 2)
            print(f"Frame {frame_id}: {pred} - {confidence}%")  # Debug output

            if pred == "Accident":
                cv2.rectangle(display, (0, 0), (300, 40), (0, 0, 0), -1)
                cv2.putText(
                    display,
                    f"{pred} {confidence}%",
                    (20, 30),
                    font,
                    1,
                    (0, 0, 255),
                    2
                )
                
                if confidence > CONFIDENCE_THRESHOLD and not alarm_triggered:
                    save_accident_photo(frame)  # Saves original full-size frame
                    alarm_triggered = True
                    start_alert_thread()

        cv2.imshow("RTSP Accident Detection", display)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    camera.stop()
    cv2.destroyAllWindows()

# ===================== ENTRY =====================
if __name__ == "__main__":
    startapplication()
