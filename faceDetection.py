from cv2 import convexHull, drawContours, cvtColor, COLOR_BGR2GRAY, COLOR_RGB2BGR, COLOR_BGR2RGB
from numpy import array
from mediapipe.python.solutions import face_detection

import scipy.signal as signal
from scipy.spatial import distance as dist
from imutils import face_utils
from time import time
from dlib import shape_predictor, rectangle

import drawing_utils

class Detection():

    def __init__(self):
        self.mp_face_detection = face_detection
        self.predictor = shape_predictor('shape_predictor_68_face_landmarks.dat')
        (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
        (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
        (self.mStart, self.mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

        self.smileThreshold = 0.3
        self.smileConsistentFrame = 2
        self.smileCounter = 0
        self.smiling = 0

        self.blinkConsistentFrame = 2
        self.leftBlink = False
        self.rightBlink = False
        self.leftCounter = 0
        self.rightCounter = 0
        self.leftTotal = 0
        self.rightTotal = 0
        self.Total = 0

        self.timer = 0
        self.frameCounter = 0
        self.FPS = 0


    def eyeAspectRatio(self, eye):
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])
        C = dist.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear

    def mouthAspectRatio(self, mouth):
        A = dist.euclidean(mouth[0], mouth[6])
        B = dist.euclidean(mouth[1], mouth[11])
        C = dist.euclidean(mouth[2], mouth[10])
        D = dist.euclidean(mouth[3], mouth[9])
        E = dist.euclidean(mouth[4], mouth[8])
        F = dist.euclidean(mouth[5], mouth[7])
        mar = (B + C + D + E + F) / (5 * A)
        return mar

    def blinkDetection(self, shape, eyeThreshold):
        leftEye = shape[self.lStart:self.lEnd]
        rightEye = shape[self.rStart:self.rEnd]
        leftEAR = self.eyeAspectRatio(leftEye)
        rightEAR = self.eyeAspectRatio(rightEye)
        leftEyeHull = convexHull(leftEye)
        rightEyeHull = convexHull(rightEye)

        drawContours(self.image, [leftEyeHull], -1, (0, 255, 0), 1)
        drawContours(self.image, [rightEyeHull], -1, (0, 255, 0), 1)

        if leftEAR < eyeThreshold:
            # if not leftClose:
            self.leftCounter += 1
        else:
            if self.leftCounter >= self.blinkConsistentFrame:
                # leftClose = True
                self.leftBlink = True
                self.leftTotal += 1

            self.leftCounter = 0

        if rightEAR < eyeThreshold:
            self.rightCounter += 1
        else:
            if self.rightCounter >= self.blinkConsistentFrame:
                self.rightBlink = True
                self.rightTotal += 1

            self.rightCounter = 0

        if self.leftBlink and self.rightBlink:
            self.Total += 1
        # cv2.putText(self.image,
        #             "leftBlinks: {}, rightBlinks: {}, bothBlinks: {}".format(self.leftTotal, self.rightTotal,
        #                                                                      self.Total),
        #             (10, 30),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        self.leftBlink = False
        self.rightBlink = False

    def smileDetection(self, shape, x1, y2):

        mouth = shape[self.mStart:self.mEnd]
        MAR = self.mouthAspectRatio(mouth)

        if MAR < self.smileThreshold:
            self.smileCounter += 1
            if self.smileCounter >= self.smileConsistentFrame:
                # cv2.putText(self.image, "Smiling", (x1, y2 + 40), fontScale=1.5,
                self.smiling = True
                self.smileCounter -= 1
        else:
            self.smiling = False


    def smileNBlinkDetection(self, x1, y1, x2, y2, eyeThreshold):
        rect = rectangle(x1, y1, x2, y2)
        gray = cvtColor(self.image, COLOR_BGR2GRAY)

        # median filter denoiseing
        denoisedGray = signal.medfilt2d(array(gray), kernel_size=3)

        shape = self.predictor(denoisedGray, rect)
        shape = face_utils.shape_to_np(shape)

        self.smileDetection(shape, x1, y2)
        self.blinkDetection(shape, eyeThreshold)

    def detection(self, image):
        # For webcam input:

        with self.mp_face_detection.FaceDetection(
                model_selection=0, min_detection_confidence=0.5) as face_detection:
            start = time()
            self.image = image
            self.frameCounter += 1


            self.image.flags.writeable = False
            self.image = cvtColor(self.image, COLOR_BGR2RGB)
            results = face_detection.process(self.image)

            # Draw the face detection annotations on the image.
            self.image.flags.writeable = True
            self.image = cvtColor(self.image, COLOR_RGB2BGR)
            (self.x, self.y, _) = self.image.shape
            if results.detections:
                for detection in results.detections:

                    (x1, y1), (x2, y2) = drawing_utils.draw_detection(self.image, detection)
                    w, h = x2 - x1, y2 - y1
                    if w * h / (self.x * self.y) > 0.05671875:
                        eyeThreshold = 0.25
                    else:
                        eyeThreshold = 0.27

                    self.smileNBlinkDetection(x1, y1, x2, y2, eyeThreshold)

            end = time()
            self.timer += end - start
            if self.frameCounter % 30 == 0 and self.frameCounter >= 30:
                # start = end
                self.FPS = int(30. / self.timer)
                self.timer = 0
                # self.frameCounter = 0

            # cv2.putText(self.image, "FPS:%d" % FPS, (self.x, 30), fontScale=0.7, fontFace=cv2.FONT_HERSHEY_SIMPLEX,
            #             color=(0, 0, 255))
            # cv2.imshow('Face Detection', self.image)

        # cap.release()
        # cv2.destroyAllWindows()

if __name__ == '__main__':
    Detection().detection()