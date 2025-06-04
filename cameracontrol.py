from PyQt6 import uic
from PyQt6.QtWidgets import QDialog
from PyQt6.QtGui import QIcon
import cv2
import platform

class CameraControlsDialog(QDialog):
    def __init__(self, camera_thread, parent=None):
        super().__init__(parent)
        uic.loadUi("ui/cameracontrols.ui", self)
        self.setWindowTitle("Camera settings")
        self.setWindowIcon(QIcon("asset/icon.png"))

        self.camera_thread = camera_thread
        self.is_windows = platform.system() == "Windows"

        self.pushButton_close.clicked.connect(self.close_dialog)

        # Brightness
        self.slider_Brightness.setRange(-64, 64)
        self.slider_Brightness.setValue(self.safe_get(cv2.CAP_PROP_BRIGHTNESS))
        self.lbl_brightness.setText(str(self.slider_Brightness.value()))

        self.slider_Brightness.valueChanged.connect(lambda v: (self.set_property(cv2.CAP_PROP_BRIGHTNESS, v),
               self.lbl_brightness.setText(str(v))))

        # Contrast
        self.slider_Contrast.setRange(0, 100)
        self.slider_Contrast.setValue(self.safe_get(cv2.CAP_PROP_CONTRAST))
        self.lbl_contrast.setText(str(self.slider_Contrast.value()))
        self.slider_Contrast.valueChanged.connect(lambda v: (self.set_property(cv2.CAP_PROP_CONTRAST, v),
               self.lbl_contrast.setText(str(v))))

        # Focus
        self.slider_Focus.setRange(0, 1023)
        self.slider_Focus.setValue(self.safe_get(cv2.CAP_PROP_FOCUS))
        self.lbl_focus.setText(str(self.slider_Focus.value()))
        self.slider_Focus.valueChanged.connect(lambda v: (self.set_property(cv2.CAP_PROP_FOCUS, v),
                self.lbl_focus.setText(str(v))))

        # Saturation
        self.slider_Saturation.setRange(0, 100)
        self.slider_Saturation.setValue(self.safe_get(cv2.CAP_PROP_SATURATION))
        self.lbl_saturation.setText(str(self.slider_Saturation.value()))
        self.slider_Saturation.valueChanged.connect(lambda v: (self.set_property(cv2.CAP_PROP_SATURATION, v),
                self.lbl_saturation.setText(str(v))))

        # Hue
        self.slider_HUE.setRange(-180, 180)
        self.slider_HUE.setValue(self.safe_get(cv2.CAP_PROP_HUE))
        self.lbl_hue.setText(str(self.slider_HUE.value()))
        self.slider_HUE.valueChanged.connect(lambda v: (self.set_property(cv2.CAP_PROP_HUE, v),
                self.lbl_hue.setText(str(v))))

        # Exposure
        if self.is_windows:
            self.slider_Exposure.setRange(-80, 0)  # Typical Windows -13 to 0 (log scale) OCAL camera ma -8.0
            init_val = (int(self.safe_get(cv2.CAP_PROP_EXPOSURE) * 10))
            self.slider_Exposure.valueChanged.connect(self.update_exposure)
            self.slider_Exposure.setValue(init_val)
            self.lbl_exposure.setText(f"{init_val / 10.0:.1f}")
            self.slider_Exposure.valueChanged.connect(self.update_exposure)
        else:
            self.slider_Exposure.setRange(1, 10000)  # Linux (e.g. microseconds)
            self.slider_Exposure.setValue(self.safe_get(cv2.CAP_PROP_EXPOSURE))
            self.lbl_exposure.setText(f"{self.slider_Exposure.value() / 10.0:.1f}")
            self.slider_Exposure.valueChanged.connect(lambda v: (self.set_property(cv2.CAP_PROP_EXPOSURE, v),
                    self.lbl_exposure.setText(f"{v:.1f}")))

        # Gamma
        self.slider_Gamma.setRange(100, 500)
        self.slider_Gamma.setValue(self.safe_get(cv2.CAP_PROP_GAMMA))
        self.lbl_gamma.setText(str(self.slider_Gamma.value()))      
        self.slider_Gamma.valueChanged.connect(lambda v: (self.set_property(cv2.CAP_PROP_GAMMA, v), 
                    self.lbl_gamma.setText(str(v))))

        # Color temperature
        self.slider_Colortemp.setRange(2800, 6500)
        self.slider_Colortemp.setValue(self.safe_get(cv2.CAP_PROP_TEMPERATURE))
        self.lbl_color_temp.setText(str(self.slider_Colortemp.value()))
        self.slider_Colortemp.valueChanged.connect(lambda v: (self.set_property(cv2.CAP_PROP_TEMPERATURE, v),
                    self.lbl_color_temp.setText(str(v))))

        # Sharpness
        self.slider_sharpness.setRange(0, 100)
        self.slider_sharpness.setValue(self.safe_get(cv2.CAP_PROP_SHARPNESS))
        self.lbl_sharpness.setText(str(self.slider_sharpness.value()))
        self.slider_sharpness.valueChanged.connect(lambda v: (self.set_property(cv2.CAP_PROP_SHARPNESS, v), 
                    self.lbl_sharpness.setText(str(v))))

        # Auto Focus
        autofocus = bool(self.get_property(cv2.CAP_PROP_AUTOFOCUS))
        self.checkBox_Auto_Focus.setChecked(autofocus)
        self.handle_auto_focus(int(autofocus))
        self.checkBox_Auto_Focus.stateChanged.connect(self.handle_auto_focus)

        # Auto Exposure
        ae_value = self.get_property(cv2.CAP_PROP_AUTO_EXPOSURE)
        is_auto_expo = ae_value >= 0.5
        self.checkBox_Auto_Exposure.setChecked(is_auto_expo)
        self.handle_auto_exposure(is_auto_expo)
        self.checkBox_Auto_Exposure.stateChanged.connect(self.handle_auto_exposure)

        # Auto White Balance
        wb_auto = bool(self.get_property(cv2.CAP_PROP_AUTO_WB))
        self.checkBox_Auto_Wbalance.setChecked(wb_auto)
        self.handle_auto_whitebalance(int(wb_auto))
        self.checkBox_Auto_Wbalance.stateChanged.connect(self.handle_auto_whitebalance)

    def close_dialog(self):
        self.close()

    def set_property(self, prop, val):
        if self.camera_thread and self.camera_thread.cap:
            self.camera_thread.cap.set(prop, float(val))
            new_val = self.get_property(prop)
            print(f"Updated {prop} to {new_val}")

    def get_property(self, prop):
        if self.camera_thread and self.camera_thread.cap:
            return self.camera_thread.cap.get(prop)
        return 0

    def safe_get(self, prop):
        """Get numeric property value. Accept negative for exposure (Windows)."""
        try:
            val = self.get_property(prop)
            if prop == cv2.CAP_PROP_EXPOSURE:
                return int(val)  # Accept negative on Windows
            return int(val) if val >= 0 else 0
        except:
            return 0

    def handle_auto_focus(self, state):
        self.set_property(cv2.CAP_PROP_AUTOFOCUS, state)
        self.slider_Focus.setEnabled(state == 0)

    def handle_auto_exposure(self, state):
        # 0.25 = manual, 0.75 = auto (Windows-style)
        val = 0.75 if state else 0.25
        self.set_property(cv2.CAP_PROP_AUTO_EXPOSURE, val)
        self.slider_Exposure.setEnabled(state == 0)

    def handle_auto_whitebalance(self, state):
        self.set_property(cv2.CAP_PROP_AUTO_WB, state)
        self.lbl_color_temp.setText("Auto" if state else str(self.slider_Colortemp.value()))
        self.slider_Colortemp.setEnabled(state == 0)
        
    def update_exposure(self, val):
        real_val = val / 10.0
        self.set_property(cv2.CAP_PROP_EXPOSURE, real_val)
        print(f"EXPOSURE {real_val}")