from PyQt5 import QtCore,QtWidgets,QtGui
from main_win.win import Ui_mainWindow

from faceDetection import Detection

from sys import argv, exit
from cv2 import VideoWriter, resize, flip, cvtColor, COLOR_BGR2RGB, imwrite, CAP_PROP_FPS, VideoWriter_fourcc
from os import makedirs, path
from time import strftime, localtime




class MainWindow():
    def __init__(self):
        app = QtWidgets.QApplication(argv)
        MainWindow = QtWidgets.QMainWindow()
        self.raw_image = None
        self.ui = Ui_mainWindow()
        self.ui.setupUi(MainWindow)
        self.action_connect()
        self.fd = Detection()
        self.enableDet = False
        self.save_fold = './result'
        self.frameCount = 0
        MainWindow.show()
        exit(app.exec_())

# 信号槽绑定
    def action_connect(self):

        self.ui.runButton.clicked.connect(self.run_or_continue)
        self.ui.fileButton.clicked.connect(self.open_file)

        self.ui.cameraButton.clicked.connect(self.button_open_camera_click)
        self.ui.resetButton.clicked.connect(self.resetCounter)
        self.ui.timer_camera.timeout.connect(self.show_camera)
        self.ui.saveCheckBox.clicked.connect(self.is_save)


    def open_file(self):
        print('to do open_file')
        # config_file = 'config/fold.json'
        # # config = json.load(open(config_file, 'r', encoding='utf-8'))
        # config = json.load(open(config_file, 'r', encoding='utf-8'))
        # open_fold = config['open_fold']
        # if not os.path.exists(open_fold):
        #     open_fold = os.getcwd()
        # name, _ = QFileDialog.getOpenFileName(None, '选取视频或图片', open_fold, "Pic File(*.mp4 *.mkv *.avi *.flv "
        #                                                                   "*.jpg *.png)")
        # if name:
        #     # self.det_thread.source = name
        #     # self.statistic_msg('加载文件：{}'.format(os.path.basename(name)))
        #     config['open_fold'] = os.path.dirname(name)
        #     config_json = json.dumps(config, ensure_ascii=False, indent=2)
        #     with open(config_file, 'w', encoding='utf-8') as f:
        #         f.write(config_json)
        #     切换文件后，上一次检测停止
        #     self.stop()

    def showCounter(self):
        self.ui.fps_label.setText('fps：' + str(self.fd.FPS))
        self.ui.label.setText(str(self.fd.smiling))
        self.ui.label_2.setText(str(self.fd.leftTotal))
        self.ui.label_3.setText(str(self.fd.rightTotal))
        self.ui.label_4.setText(str(self.fd.Total))


    def show_camera(self):
        flag, self.camera_image = self.ui.cap.read()
        self.frameCount += 1

        if self.enableDet:
            self.fd.detection(self.camera_image)
            img_src = self.fd.image
        else:
            img_src = self.camera_image

        ih, iw, _ = img_src.shape
        w = self.ui.out_video.geometry().width()
        h = self.ui.out_video.geometry().height()

        if iw > ih:
            scal = w / iw
            nw = w
            nh = int(scal * ih)
            img_src_ = resize(img_src, (nw, nh))

        else:
            scal = h / ih
            nw = int(scal * iw)
            nh = h
            img_src_ = resize(img_src, (nw, nh))

        img_src_ = flip(img_src_, 1)

        show = cvtColor(img_src_, COLOR_BGR2RGB)

        self.autoSave(img_src_)

        showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], show.shape[2] * show.shape[1], QtGui.QImage.Format_RGB888)
        self.ui.out_video.setPixmap(QtGui.QPixmap.fromImage(showImage))

        self.showCounter()

    def resetCounter(self):
        self.fd.smiling = False
        self.fd.leftTotal = 0
        self.fd.rightTotal = 0
        self.fd.Total = 0
        self.showCounter()

    def is_save(self):
        if self.ui.saveCheckBox.isChecked():
            self.save_fold = './result'
        else:
            self.save_fold = None

    def autoSave(self, img):

        if self.save_fold:
            makedirs(self.save_fold, exist_ok=True)  # 路径不存在，自动保存
            # 如果输入是图片
            if self.ui.cap is None:
                save_path = path.join(self.save_fold,
                                         strftime('%Y_%m_%d_%H_%M_%S',
                                                       localtime()) + '.jpg')
                imwrite(save_path, img)
            else:
                if self.frameCount == 1:  # 第一帧时初始化录制
                    # 以视频原始帧率进行录制
                    ori_fps = int(self.ui.cap.get(CAP_PROP_FPS))
                    if ori_fps == 0:
                        ori_fps = 25
                    width, height = img.shape[1], img.shape[0]
                    save_path = path.join(self.save_fold,
                                             strftime('%Y_%m_%d_%H_%M_%S', localtime()) + '.mp4')
                    self.out = VideoWriter(save_path, VideoWriter_fourcc(*"mp4v"), ori_fps,
                                               (width, height))
                if self.frameCount > 0:
                    self.out.write(img)

    def button_open_camera_click(self):
        if self.ui.cameraButton.isChecked():
            if self.ui.cap.isOpened():
                self.ui.cap.release()
            if self.ui.timer_camera.isActive():
                self.ui.timer_camera.stop()

            if self.ui.timer_camera.isActive() == False:
                flag = self.ui.cap.open(0)
                if flag == False:
                    msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"没有检测到相机",
                                                        buttons=QtWidgets.QMessageBox.Ok,
                                                        defaultButton=QtWidgets.QMessageBox.Ok)
                else:
                    self.ui.timer_camera.start(20)
        else:
            self.ui.timer_camera.stop()
            self.ui.cap.release()
            self.ui.out_video.clear()

    def run_or_continue(self):
        if self.ui.runButton.isChecked():
            self.enableDet = True
        else:
            self.enableDet = False


if __name__ == "__main__":
    MainWindow()
