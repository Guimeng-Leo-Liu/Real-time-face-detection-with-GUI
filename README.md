# Real-time-face-detection-with-GUI
A application with face detection + smile detection + eyes blink detection using pyqt5

This repository can achieve 70+FPS in a CPU-only environment


**Watch example video:**  
(https://www.bilibili.com/video/BV1Be4y1U7xg/?vd_source=780f68563562773e81e029d34afe9157)

## Setup and installation
```bash
# create and activate new conda environment
conda create --name GUI python=3.7
conda activate GUI

# install required packages
pip install opencv-python PyQt5 PyQt5-tools scipy numpy mediapipe imutils cmake boost dlib

# clone the repository
git clone https://github.com/Guimeng-Leo-Liu/Real-time-face-detection-with-GUI.git
```

## Run program

```bash
# lanuch GUI
python main.py


# run only detection models
cd ./faceDetection/
python webcamFaceDetection.py
```
