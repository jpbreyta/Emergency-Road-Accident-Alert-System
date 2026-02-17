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
    """
    Save accident photo with full resolution and optional timestamp overlay.
    
    Args:
        frame: Original full-size frame from camera (not resized)
        directory: Directory to save photos
    
    Returns:
        filename: Path to saved photo or None if failed
    """
    try:
        os.makedirs(directory, exist_ok=True)
        
        # Create a copy to avoid modifying the original frame
        photo = frame.copy()
        
        # Add timestamp and label overlay for better documentation
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        # Add semi-transparent background for text
        overlay = photo.copy()
        cv2.rectangle(overlay, (10, 10), (500, 80), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, photo, 0.4, 0, photo)
        
        # Add text
        cv2.putText(photo, "ACCIDENT DETECTED", (20, 35), font, 0.8, (0, 0, 255), 2)
        cv2.putText(photo, timestamp, (20, 65), font, 0.6, (255, 255, 255), 2)
        
        # Save with high quality
        filename = os.path.join(directory, time.strftime("%Y-%m-%d-%H%M%S") + ".jpg")
        cv2.imwrite(filename, photo, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        print(f"📸 Accident photo saved: {filename} ({photo.shape[1]}x{photo.shape[0]} pixels)")
        return filename
    except Exception as e:
        print(f"⚠️ Photo save error: {e}")
        return None