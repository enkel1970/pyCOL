from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QIcon
import cv2

class CameraControlsDialog(QDialog):
    def __init__(self, camera_thread, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/cameracontrols.ui", self)
        self.setWindowTitle("Camera settngs")
        self.setWindowIcon(QIcon("asset/icon.png"))

        self.camera_thread = camera_thread

        self.pushButton_close.clicked.connect(self.close_dialog)

        # Brightness slider
        self.slider_Brightness.setRange(-64, 64)
        self.slider_Brightness.setValue(int(self.get_property(cv2.CAP_PROP_BRIGHTNESS)))
        self.slider_Brightness.valueChanged.connect(lambda value: self.set_property(cv2.CAP_PROP_BRIGHTNESS, value))

        # Contrast slider
        self.slider_Contrast.setRange(0, 100)
        self.slider_Contrast.setValue(int(self.get_property(cv2.CAP_PROP_CONTRAST)))
        self.slider_Contrast.valueChanged.connect(lambda value: self.set_property(cv2.CAP_PROP_CONTRAST, value))

        # Focus slider
        self.slider_Focus.setRange(0, 1023)
        self.slider_Focus.setValue(int(self.get_property(cv2.CAP_PROP_FOCUS)))
        self.slider_Focus.valueChanged.connect(lambda value: self.set_property(cv2.CAP_PROP_FOCUS, value))

        # Saturation slider
        self.slider_Saturation.setRange(0, 100)
        self.slider_Saturation.setValue(int(self.get_property(cv2.CAP_PROP_SATURATION)))
        self.slider_Saturation.valueChanged.connect(lambda value: self.set_property(cv2.CAP_PROP_SATURATION, value))

        # Exposure slider
        self.slider_Exposure.setRange(50, 10000)
        self.slider_Exposure.setValue(int(self.get_property(cv2.CAP_PROP_EXPOSURE)))
        self.slider_Exposure.valueChanged.connect(lambda value: self.set_property(cv2.CAP_PROP_EXPOSURE, value))

        # Gamma slider
        self.slider_Gamma.setRange(0, 500)
        self.slider_Gamma.setValue(int(self.get_property(cv2.CAP_PROP_GAMMA)))
        self.slider_Gamma.valueChanged.connect(lambda value: self.set_property(cv2.CAP_PROP_GAMMA, value))

        # Temperature slider
        self.slider_Colortemp.setRange(2800, 6500)
        self.slider_Colortemp.setValue(int(self.get_property(cv2.CAP_PROP_TEMPERATURE)))
        self.slider_Colortemp.valueChanged.connect(lambda value: self.set_property(cv2.CAP_PROP_TEMPERATURE, value))

        # White Balance slider currently unsupported in OpenCV
        # self.slider_Wbalance.setEnabled(False)
        # self.slider_Wbalance.setRange(-5, 5)
        # self.slider_Wbalance.setValue(int(self.get_property(cv2.CAP_PROP_WB_TEMPERATURE)))
        # self.slider_Wbalance.valueChanged.connect(lambda value: self.set_property(cv2.CAP_PROP_WB_TEMPERATURE, value))

        # checkBox_AutoFocus
        focus_auto = bool(self.get_property(cv2.CAP_PROP_AUTOFOCUS))
        self.checkBox_Auto_Focus.setChecked(focus_auto)
        self.handle_auto_focus(int(focus_auto))  # aggiorna lo slider
        self.checkBox_Auto_Focus.stateChanged.connect(self.handle_auto_focus)

        # checkBox_AutoExposure
        exposure_auto = bool(self.get_property(cv2.CAP_PROP_AUTO_EXPOSURE))
        self.checkBox_Auto_Exposure.setChecked(exposure_auto)
        self.handle_auto_exposure(int(exposure_auto))   
        self.checkBox_Auto_Exposure.stateChanged.connect(self.handle_auto_exposure)

        # checkBox_AutoWhiteBalance
        wb_auto = bool(self.get_property(cv2.CAP_PROP_AUTO_WB))
        # self.checkBox_Auto_Wbalance.setChecked(wb_auto)
        self.handle_auto_whitebalance(int(wb_auto))  # aggiorna lo slider
        self.checkBox_Auto_Wbalance.stateChanged.connect(self.handle_auto_whitebalance)

        # Sharpness slider
        self.slider_sharpness.setRange(0, 100)
        self.slider_sharpness.setValue(int(self.get_property(cv2.CAP_PROP_SHARPNESS)))
        self.slider_sharpness.valueChanged.connect(lambda value: self.set_property(cv2.CAP_PROP_SHARPNESS, value))

        # Hue slider
        self.slider_HUE.setRange(0, 180)
        self.slider_HUE.setValue(int(self.get_property(cv2.CAP_PROP_HUE)))
        self.slider_HUE.valueChanged.connect(lambda value: self.set_property(cv2.CAP_PROP_HUE, value))

    def close_dialog(self):
        self.close()

    def set_property(self, prop, val):
        if self.camera_thread and self.camera_thread.cap:
            self.camera_thread.cap.set(prop, float(val))
            val = self.get_property(prop)
            print(f"Updated {prop} at {val}")
    
    def get_property(self, prop):
        if self.camera_thread and self.camera_thread.cap:
            return self.camera_thread.cap.get(prop)
        return 0

    def handle_auto_focus(self, state):
        self.set_property(cv2.CAP_PROP_AUTOFOCUS, state)
        self.slider_Focus.setEnabled(state == 0)  # Enable focus slider only if autofocus is off

    def handle_auto_exposure(self, state):
        self.set_property(cv2.CAP_PROP_AUTO_EXPOSURE, state)
        self.slider_Exposure.setEnabled(state == 0)

    def handle_auto_whitebalance(self, state):
        self.set_property(cv2.CAP_PROP_AUTO_WB, state)
        # self.slider_Wbalance.setEnabled(state == 0)