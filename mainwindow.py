from PyQt6.QtWidgets import QMainWindow, QApplication, QColorDialog, QLabel
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QColor
import cv2, os
from videowindow import VideoWindow
from camera import find_camera_index_by_name_substring
from cameracontrol import CameraControlsDialog

class CameraThread(QThread):
    frameCaptured = pyqtSignal(object)

    def __init__(self, camera_index=None):
        super().__init__()
        self.camera_index = camera_index
        print(f"Inizializzazione thread camera con indice {self.camera_index}")
        self.running = False
        self.cap = None
                
    def run(self):
        self.cap = cv2.VideoCapture(2, cv2.CAP_V4L2)
        
        # Imposta MJPEG esplicitamente
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc(*'MJPG'))
        self.cap.set(cv2.CAP_PROP_SETTINGS, 1)  # Imposta MJPEG come formato di codifica
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

        # normalizza il percorso del file
        asset_file_path = os.path.join(os.path.dirname(__file__), 'asset', 'logo.png')

        #self.ui.setIcon(QIcon(asset_file_path))
        logo = QPixmap(asset_file_path)
        self.ui.lbl_Logo.setPixmap(logo)
      
        # Collegamenti pulsanti
        self.ui.btnOpenCamera.clicked.connect(self.start_camera)
        self.ui.btnCloseCamera.clicked.connect(self.stop_camera)
        self.ui.btnCameraSettings.clicked.connect(self.open_camera_control_dialog)
        self.ui.btn_exit.clicked.connect(self.close)

        # Collegamento slider offset X, Y e checkbox per abilitare offset
        self.ui.sliderOffsetX.setRange(-20, 20)
        self.ui.sliderOffsetY.setRange(-20, 20)
        self.ui.sliderOffsetX.setValue(0)
        self.ui.sliderOffsetY.setValue(0)

        # Collega segnali controlli offset
        self.ui.sliderOffsetX.valueChanged.connect(self.update_overlay_offset)
        self.ui.sliderOffsetY.valueChanged.connect(self.update_overlay_offset)
        self.ui.checkBoxOffset.stateChanged.connect(self.toggle_overlay_offset)

        # Collega segnale controlli croce
        self.ui.checkBox_4.stateChanged.connect(self.cross_visibility_changed)
        self.ui.sliderCrossLength.valueChanged.connect(self.cross_length_changed)
        self.ui.sliderThicknessCross.valueChanged.connect(self.cross_thickness_changed)
        self.ui.sliderCrossAngle.valueChanged.connect(self.cross_angle_changed)

        # Oggetti di stato
        self.camera_thread = None
        self.video_window = None

        # Collegamento controlli cerchi
        self.connect_overlay_controls()

        self.setup_color_labels()


    def setup_color_labels(self):
        for i in range(1, 5):  
            label = getattr(self.ui, f"label_color_{i}")
            label.setToolTip("Click to pick color")
            label.mousePressEvent = lambda event, l=label: self.pick_color_for_label(l)

    def connect_overlay_controls(self):
        # Cerchio 1
        self.ui.sliderRadius_1.valueChanged.connect(lambda val: self.update_circle(0, radius=val))
        self.ui.sliderThickness_1.valueChanged.connect(lambda val: self.update_circle(0, thickness=val))
        self.ui.checkBox_1.stateChanged.connect(lambda state: self.update_circle(0, visible=(state == 2)))

        # Cerchio 2
        self.ui.sliderRadius_2.valueChanged.connect(lambda val: self.update_circle(1, radius=val))
        self.ui.sliderThickness_2.valueChanged.connect(lambda val: self.update_circle(1, thickness=val))
        self.ui.checkBox_2.stateChanged.connect(lambda state: self.update_circle(1, visible=(state == 2)))

        # Cerchio 3
        self.ui.sliderRadius_3.valueChanged.connect(lambda val: self.update_circle(2, radius=val))
        self.ui.sliderThickness_3.valueChanged.connect(lambda val: self.update_circle(2, thickness=val))
        self.ui.checkBox_3.stateChanged.connect(lambda state: self.update_circle(2, visible=(state == 2)))    
    
    # Metodi handler croce
    def cross_visibility_changed(self, state):
        visible = (state == 2)  # 2 = checked
        if self.video_window:
            self.video_window.set_cross_property('visible', visible)

    def cross_length_changed(self, val):
        if self.video_window:
            self.video_window.set_cross_property('length', val)

    def cross_thickness_changed(self, val):
        if self.video_window:
            self.video_window.set_cross_property('thickness', val)

    def cross_angle_changed(self, val):
        if self.video_window:
            self.video_window.set_cross_property('angle', val)
    
    def cross_color_changed(self, color):
        if self.video_window:
            self.video_window.set_cross_property('color', color)


    def pick_color_for_label(self, label: QLabel):
        current_color = label.palette().color(label.backgroundRole())
        color = QColorDialog.getColor(initial=current_color, parent=self)
        print(label.objectName(), color)
        if color.isValid():
            r, g, b = color.red(), color.green(), color.blue()
            label.setFixedSize(30, 30)
            # Aggiorna lo stile come cerchio (border-radius = metà larghezza)
            label.setStyleSheet(f"""
                background-color: rgb({r}, {g}, {b});    
                border-radius: 15px;
            """)

            if label.objectName() == "label_color_4":
                self.cross_color_changed(color)
            else:
                index = int(label.objectName().split('_')[-1]) - 1
                self.set_circle_property(index, 'color', color)
                self.update_circle(index, color=color)
            



    # Metodi handler cerchi
    def update_overlay_offset(self):
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
         
    # Metodi per avviare e fermare la camera    
    def start_camera(self):
        if self.camera_thread:
            return
        # Trova l'indice della camera
        camera_index = find_camera_index_by_name_substring()
        if camera_index is None:
            print("No camera OCAL 2 found.")
            return
        else:
            print(f"Start camera with index {camera_index}")
            # Initialize the camera thread and video window
            self.camera_thread = CameraThread(camera_index)
            self.camera_thread.frameCaptured.connect(self.update_frame)
            self.camera_thread.start()
            self.video_window = VideoWindow()

            center_offset = self.read_focus_offset()
            print(f"Offset letto da file: {center_offset}")
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

    # Ferma la camera e chiude la finestra video
    def stop_camera(self):
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread = None
        if self.video_window:
            self.video_window.close()
            self.video_window = None

    def update_frame(self, frame):
        if self.video_window:
            self.video_window.set_frame(frame)

    def update_cross(self, length=None, thickness=None, angle=None, visible=None):
        if self.video_window:
            self.video_window.set_cross_property('length', length)
            self.video_window.set_cross_property('thickness', thickness)
            self.video_window.set_cross_property('angle', angle)
            self.video_window.set_cross_property('visible', visible)

    def update_circle(self, index, radius=None, color=None, thickness=None, visible=None):
        if self.video_window:
            self.video_window.update_circle(index, radius, color, thickness, visible)

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

    def find_camera_property_range(self, cap, prop_id, test_min=0.0, test_max=1.0, steps=20):
        last_valid = test_min
        step_size = (test_max - test_min) / steps

        for i in range(steps + 1):
            val = test_min + i * step_size
            cap.set(prop_id, val)
            actual_val = cap.get(prop_id)
            if abs(actual_val - val) / max(val, 0.0001) < 0.05:
                last_valid = val
            else:
                break
        return (test_min, last_valid)
    

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


