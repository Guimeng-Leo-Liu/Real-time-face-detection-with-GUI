# Real-time-face-detection-with-GUI
A application with face detection + smile detection + eyes blink detection using pyqt5

## Setup and Installation
```bash
# create and activate new conda environment
conda create --name GUI python=3.7
conda activate GUI

# install required packages
pip install sys opencv-python PyQt5 PyQt5-tools scipy numpy mediapipe imutils cmake boost dlib

# clone the repository
git clone https://github.com/Guimeng-Leo-Liu/Real-time-face-detection-with-GUI.git
cd ./DeFlow/
```

```bash
# lanuch GUI
python main.py

# run only detection models
cd ./faceDetection/
python webcamFaceDetection.py
```
