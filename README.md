





https://github.com/user-attachments/assets/69ecddbf-3db9-43bb-9c0e-81497fb50600






# Road Accident Detection & Alert System

# How to Start?

1. Open Visual Studio Code and Open a Terminal and Execute the Following:
> [!NOTE]
> This is to clone the project to your system
```
git clone https://github.com/jared27906/SJRoad.git
```

2. Setup a Python Environment:
> [!NOTE]
> You should see (venv) pop-up in the Terminal, if it does pop up, It means it worked :D
```
python -m venv venv
venv\Scripts\activate
```

3. Install all requirements/packages:
> [!NOTE]
> This part is important, without this, running the main.py won't work.
```
pip install --upgrade pip
pip install -r imports.txt
```

4. Install the model data:
https://www.mediafire.com/file/hdwt1onaba581uq/model_weights.h5/file

5. Find the `SJRoad Repository` in Your File Manager and Paste in the `model_weights.h5` file

6. Edit the `camera.py` to initialize the RTSP system (`Line 138`):
> [!NOTE]
> Example: `cam = "rtsp://114270929:Ttabataba123@10.190.29.172:554/live/ch00_0"`
```
cam = "rtsp://CameraID:CameraPassword@CameraIPAddress:554/live/ch00_0"
```

7. Run the following command:
```
python main.py  
```

Kapag need niyo pa ng help, message niyo ako.
