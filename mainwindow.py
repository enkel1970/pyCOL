from PyQt6.QtWidgets import QMainWindow, QApplication, QColorDialog, QLabel, QMessageBox
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap
import cv2, os, platform
from videowindow import VideoWindow
from camera import find_camera_index_by_name_substring
from cameracontrol import CameraControlsDialog

class CameraThread(QThread):
    frameCaptured = pyqtSignal(object)

    def __init__(self, camera_index=None):
        super().__init__()
        self.camera_index = camera_index
        print(f"Init thread camera with index {self.camera_index}")
        self.running = False
        self.cap = None
                
    def run(self):
        # select the appropriate backend based on the platform
        platform_name = platform.system().lower()
        if platform_name == 'windows':
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_DSHOW)
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)  # Set manual exposure
            self.cap.set(cv2.CAP_PROP_EXPOSURE, -4)  # Set exposure to a reasonable value
        elif platform_name == 'darwin':
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_AVFOUNDATION)
        elif platform_name == 'linux':
            self.cap = cv2.VideoCapture(self.camera_index, cv2.CAP_V4L2)
        else:
            raise RuntimeError(f"Unsupported platform: {platform_name}")
        
        # Set MJPEG codec and resolution
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3264)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2448)

        self.running = self.cap.isOpened()
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                self.frameCaptured.emit(frame)
        self.cap.release()
        self.cap = None

    def stop(self):
        self.running = False
        self.wait()


class MainWindow(QMainWindow):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.controls_dialog = None

        # normalize the path of the .ui file
        asset_file_path = os.path.join(os.path.dirname(__file__), 'asset', 'logo.png')
        logo = QPixmap(asset_file_path)
        self.ui.lbl_Logo.setPixmap(logo)
      
        # Event handlers for buttons
        self.ui.btnOpenCamera.clicked.connect(self.start_camera)
        self.ui.btnCloseCamera.clicked.connect(self.stop_camera)
        self.ui.btnCameraSettings.clicked.connect(self.open_camera_control_dialog)
        self.ui.btn_exit.clicked.connect(self.close)

        # set the min and max values for offset slider
        self.ui.sliderOffsetX.setRange(-20, 20)
        self.ui.sliderOffsetY.setRange(-20, 20)

        # set initial values for offset sliders
        self.ui.sliderOffsetX.setValue(0)
        self.ui.sliderOffsetY.setValue(0)

        # Event handlers for offset sliders and checkbox
        self.ui.sliderOffsetX.valueChanged.connect(self.update_overlay_offset)
        self.ui.sliderOffsetY.valueChanged.connect(self.update_overlay_offset)
        self.ui.checkBoxOffset.stateChanged.connect(self.toggle_overlay_offset)

        # Event handlers for cross sliders and checkbox
        self.ui.checkBox_4.stateChanged.connect(self.cross_visibility_changed)
        self.ui.sliderCrossLength.valueChanged.connect(self.cross_length_changed)
        self.ui.sliderThicknessCross.valueChanged.connect(self.cross_thickness_changed)
        self.ui.sliderCrossAngle.valueChanged.connect(self.cross_angle_changed)

        # Objects for camera and video window
        self.camera_thread = None
        self.video_window = None

        # set Events for circles sliders and checkboxes
        self.connect_overlay_controls()

        self.setup_color_labels()

        self.ui.setStyleSheet(f"""
            QSlider::handle:horizontal {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }}
            QSlider::groove:horizontal {{
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0, stop:0 rgba(128, 128, 128, 255), stop:1 rgba(255, 255, 255, 255));
                height: 8px;
                border-radius: 3px;
            }}
        """)

        # Set the initial values for cross properties
        self.ui.lbl_r1.setText(str(self.ui.sliderRadius_1.value()))
        self.ui.lbl_t1.setText(str(self.ui.sliderThickness_1.value()))
        self.ui.lbl_r2.setText(str(self.ui.sliderRadius_2.value()))
        self.ui.lbl_t2.setText(str(self.ui.sliderThickness_2.value()))
        self.ui.lbl_r3.setText(str(self.ui.sliderRadius_3.value()))
        self.ui.lbl_t3.setText(str(self.ui.sliderThickness_3.value()))
        self.ui.lbl_x.setText(str(self.ui.sliderOffsetX.value()))
        self.ui.lbl_y.setText(str(self.ui.sliderOffsetY.value()))
        self.ui.lbl_cl.setText(str(self.ui.sliderCrossLength.value()))
        self.ui.lbl_ct.setText(str(self.ui.sliderThicknessCross.value()))
        self.ui.lbl_ca.setText(str(self.ui.sliderCrossAngle.value()))
       
    def setup_color_labels(self):
        for i in range(1, 5):  
            label = getattr(self.ui, f"label_color_{i}")
            label.mousePressEvent = lambda event, l=label: self.pick_color_for_label(l)

    def connect_overlay_controls(self):
        # Circle 1 and checkbox 
        self.ui.sliderRadius_1.valueChanged.connect(lambda val: (self.update_circle(0, radius=val), self.ui.lbl_r1.setText(str(val))))
        self.ui.sliderThickness_1.valueChanged.connect(lambda val: (self.update_circle(0, thickness=val), self.ui.lbl_t1.setText(str(val))))
        self.ui.checkBox_1.stateChanged.connect(lambda state: self.update_circle(0, visible=(state == 2)))

        # Circle 2 and checkbox
        self.ui.sliderRadius_2.valueChanged.connect(lambda val: (self.update_circle(1, radius=val), self.ui.lbl_r2.setText(str(val))))
        self.ui.sliderThickness_2.valueChanged.connect(lambda val: (self.update_circle(1, thickness=val), self.ui.lbl_t2.setText(str(val))))
        self.ui.checkBox_2.stateChanged.connect(lambda state: self.update_circle(1, visible=(state == 2)))

        # Circle 3 and checkbox
        self.ui.sliderRadius_3.valueChanged.connect(lambda val: (self.update_circle(2, radius=val), self.ui.lbl_r3.setText(str(val))))
        self.ui.sliderThickness_3.valueChanged.connect(lambda val: (self.update_circle(2, thickness=val), self.ui.lbl_t3.setText(str(val))))
        self.ui.checkBox_3.stateChanged.connect(lambda state: self.update_circle(2, visible=(state == 2)))    
    
    # Methods for cross properties changes
    def cross_visibility_changed(self, state):
        visible = (state == 2)  # 2 = checked
        if self.video_window:
            self.video_window.set_cross_property('visible', visible)

    def cross_length_changed(self, val):
        self.ui.lbl_cl.setText(str(val))
        if self.video_window:
            self.video_window.set_cross_property('length', val)

    def cross_thickness_changed(self, val):
        self.ui.lbl_ct.setText(str(val))
        if self.video_window:
            self.video_window.set_cross_property('thickness', val)

    def cross_angle_changed(self, val):
        self.ui.lbl_ca.setText(str(val))
        if self.video_window:
            self.video_window.set_cross_property('angle', val)
    
    def cross_color_changed(self, color):
        if self.video_window:
            self.video_window.set_cross_property('color', color)

    # Methods for picking color for circles and cross color
    def pick_color_for_label(self, label: QLabel):
        current_color = label.palette().color(label.backgroundRole())
        color = QColorDialog.getColor(initial=current_color, parent=self)
        print(label.objectName(), color)
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            label.setFixedSize(30, 30)
            # Update the label background color
            label.setStyleSheet(f"""
                background-color: rgb({r}, {g}, {b});
                border: 3px solid black;
                border-radius: 15px;  /* Make it circular */   
            """)
            # if the label is for cross color, update the cross color and its label
            if label.objectName() == "label_color_4":
                self.cross_color_changed(color)
            else: # if the label is for circles, update the corresponding circle color
                index = int(label.objectName().split('_')[-1]) - 1
                self.set_circle_property(index, 'color', color)
                self.update_circle(index, color=color)

    # Handlers for overlay offset
    def update_overlay_offset(self):
        self.ui.lbl_x.setText(str(self.ui.sliderOffsetX.value()))
        self.ui.lbl_y.setText(str(self.ui.sliderOffsetY.value()))
        if self.video_window and self.ui.checkBoxOffset.isChecked():
            x = self.ui.sliderOffsetX.value()
            y = self.ui.sliderOffsetY.value()
            self.video_window.set_center_offset(x, y)

    def toggle_overlay_offset(self, state):
        enabled = (state == 2)  # 2 = checked
        if self.video_window:
            self.video_window.set_offset_enabled(enabled)
            if enabled:
                self.update_overlay_offset()
            else:
                self.video_window.set_center_offset(0, 0)  # reset offset

    def read_focus_offset(self, path="focus.txt"):
        try:
            with open(path, 'r') as f:
                parts = f.read().strip().split()
                if len(parts) >= 4:
                    x_offset = float(parts[2])
                    y_offset = float(parts[3])
                    return (x_offset, y_offset)
        except Exception as e:
            print(f"Errore lettura offset da {path}: {e}")
        return (0.0, 0.0)
         
    """ Methods to start and stop the camera
        Start the camera and initialize the video window
        If the camera is already running, do nothing
        If the camera is not found, show a warning message
        If the camera is found, start the camera thread and show the video window
        and set the center focus offset from the file set the properties for circles and cross """  
    def start_camera(self):
        if self.camera_thread:
            return
        # Trova l'indice della camera
        camera_index = find_camera_index_by_name_substring()
        
        if camera_index is None:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setText("No campatible camera found.")
            msg.setWindowTitle("Camera Error")
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
            return
        
        else:
            print(f"Start camera with index {camera_index}")
            # Initialize the camera thread and video window
            self.camera_thread = CameraThread(camera_index)
            self.camera_thread.frameCaptured.connect(self.update_frame)
            self.camera_thread.start()
            self.video_window = VideoWindow()

            center_offset = self.read_focus_offset()
            print(f"Read offset parameter from: {center_offset}")
            self.video_window.set_center_focus(center_offset[0], center_offset[1])

            # set properties for circles and cross
            self.video_window.set_circle_property(0, 'radius', self.ui.sliderRadius_1.value())
            self.video_window.set_circle_property(0, 'thickness', self.ui.sliderThickness_1.value())
            self.video_window.set_circle_property(0, 'visible', self.ui.checkBox_1.isChecked())
            self.video_window.set_circle_property(1, 'radius', self.ui.sliderRadius_2.value())
            self.video_window.set_circle_property(1, 'thickness', self.ui.sliderThickness_2.value())
            self.video_window.set_circle_property(1, 'visible', self.ui.checkBox_2.isChecked())
            self.video_window.set_circle_property(2, 'radius', self.ui.sliderRadius_3.value())
            self.video_window.set_circle_property(2, 'thickness', self.ui.sliderThickness_3.value())
            self.video_window.set_circle_property(2, 'visible', self.ui.checkBox_3.isChecked())
            self.video_window.set_cross_property('length', self.ui.sliderCrossLength.value())
            self.video_window.set_cross_property('thickness', self.ui.sliderThicknessCross.value())
            self.video_window.set_cross_property('angle', self.ui.sliderCrossAngle.value())
            self.video_window.set_cross_property('visible', self.ui.checkBox_4.isChecked())
            self.video_window.set_cross_property('color', getattr(self.ui, 'label_color_4').palette().color(getattr(self.ui, 'label_color_4').backgroundRole()))
            self.video_window.show()
            self.ui.btnOpenCamera.setEnabled(False)  # Disable the button to prevent multiple clicks

    # Stop the camera thread and close the video window
    def stop_camera(self):
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None
        if self.video_window:
            self.video_window.close()
            self.video_window = None
            self.ui.btnOpenCamera.setEnabled(True)  # Re-enable the button
            
    # Update the video frame in the video window
    def update_frame(self, frame):
        if self.video_window:
            self.video_window.set_frame(frame)

    # Update the cross properties in the video window
    def update_cross(self, length=None, thickness=None, angle=None, visible=None):
        if self.video_window:
            self.video_window.set_cross_property('length', length)
            self.video_window.set_cross_property('thickness', thickness)
            self.video_window.set_cross_property('angle', angle)
            self.video_window.set_cross_property('visible', visible)

    def update_circle(self, index, radius=None, color=None, thickness=None, visible=None):
        if self.video_window:
            self.video_window.update_circle(index, radius, color, thickness, visible)
            print(f"Updated circle {index} with radius={radius}, color={color}, thickness={thickness}, visible={visible}")

    def set_zoom(self, zoom_value):
        if self.video_window:
            self.video_window.set_zoom(zoom_value)

    def set_circle_property(self, index, prop, value):
        if self.video_window:
            self.video_window.set_circle_property(index, prop, value)

    def toggle_offset_enabled(self, state):
        enabled = state == 2  # 2 == checked
        if self.video_window:
            self.video_window.set_offset_enabled(enabled)
            if not enabled:
                self.video_window.set_center_offset(0, 0)
                self.ui.sliderOffsetX.blockSignals(True)
                self.ui.sliderOffsetY.blockSignals(True)
                self.ui.sliderOffsetX.setValue(0)
                self.ui.sliderOffsetY.setValue(0)
                self.ui.sliderOffsetX.blockSignals(False)
                self.ui.sliderOffsetY.blockSignals(False)

    def update_center_offset(self):
        if self.video_window and self.ui.checkBoxOffset.isChecked():
            x = self.ui.sliderOffsetX.value()
            y = self.ui.sliderOffsetY.value()
            self.video_window.set_center_offset(x, y)

    def open_camera_control_dialog(self):
        if not self.controls_dialog:
            self.controls_dialog = CameraControlsDialog(camera_thread=self.camera_thread, parent=self)
        self.controls_dialog.show()
    
    def closeEvent(self, event):
        
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait() 
            self.camera_thread = None
        if self.video_window:
            self.video_window.close()
            self.video_window = None
        if self.controls_dialog:
            self.controls_dialog.close()
            self.controls_dialog = None
        event.accept()
        QApplication.quit()


