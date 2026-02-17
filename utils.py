import cv2
import os
import time
import tensorflow as tf

def setup_gpu():
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print("✅ TensorFlow GPU enabled")
            return True
        except RuntimeError as e:
            print(f"⚠️ GPU setup error: {e}")
            return False
    else:
        print("⚠️ TensorFlow running on CPU")
        return False

def preprocess_frame(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    roi = cv2.resize(rgb, (250, 250))
    roi = roi.astype("float32") / 255.0
    return roi

def save_accident_photo(frame, directory="accident_photos"):
    try:
        os.makedirs(directory, exist_ok=True)
        filename = os.path.join(directory, time.strftime("%Y-%m-%d-%H%M%S") + ".jpg")
        cv2.imwrite(filename, frame)
        print(f"📸 Accident photo saved: {filename}")
        return filename
    except Exception as e:
        print(f"⚠️ Photo save error: {e}")
        return None