import math, os
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QIcon
from PyQt6.QtCore import Qt, QPoint

import cv2
import numpy as np

class VideoWindow(QWidget):
    def __init__(self):
        super().__init__()
        # imposta il colore di sfondo della finestra
        self.setStyleSheet("background-color: black;")


        # Initialize the video frame
        self.frame = None
        self.zoom_factor = 0.39 # zoom base

        # Overlay properties for 3 circles (default)
        self.circles = [
            {'radius': 500, 'thickness': 2, 'visible': False, 'color': QColor(255, 0, 0)},   # Raggio 1 rosso
            {'radius': 250, 'thickness': 2, 'visible': False, 'color': QColor(0, 255, 0)},   # Raggio 2 verde
            {'radius': 100, 'thickness': 2, 'visible': False, 'color': QColor(0, 0, 255)},   # Raggio 3 blu
        ]

        # Proprietà croce overlay (default)
        self.cross = {
            'visible': False,
            'length': 100,        # axis length in pixels
            'thickness': 2,       # line thickness in pixels
            'angle': 0,           # angle in degrees
            'color': QColor(85, 0, 127),  # defalt purple color
        }

        # Centro di taratura dal file Ocal (x,y) in pixel, inizialmente angolo in alto a sinistra
        self.center_focus = (0,0)
        
        # Offset di spostamento overlay (x,y)
        self.center_offset = (0, 0)
        self.offset_enabled = False

        # Dimensione finestra
        self.setMinimumSize(1280, 960)

        self.setWindowTitle("Collimator Window")

        # Imposta l'icona della finestra
        icon_path = os.path.join(os.path.dirname(__file__), 'asset', 'icon.png')
        self.setWindowIcon(QIcon(icon_path))
        
    def set_frame(self, frame):
        """Aggiorna il frame da visualizzare e ridisegna la finestra."""
        self.frame = frame
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.frame is not None:
            rgb_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qimg = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)

            scaled_width = int(self.zoom_factor * w)
            scaled_height = int(self.zoom_factor * h)
            pixmap = QPixmap.fromImage(qimg).scaled(scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio)
            pixmap_x = (self.width() - pixmap.width()) // 2
            pixmap_y = (self.height() - pixmap.height()) // 2

            painter.drawPixmap(pixmap_x, pixmap_y, pixmap)

            # Calcolo corretto del centro in base a center_focus
            center_x = pixmap_x + int(self.center_focus[0] * self.zoom_factor)
            center_y = pixmap_y + int(self.center_focus[1] * self.zoom_factor)

            # Disegna lo zoom factor in alto a sinistra
            zoom_text = f"Zoom: {self.zoom_factor:.2f}x"
            font = painter.font()
            font.setPointSize(14)
            painter.setFont(font)
            
            text_margin = 10
            text_color = QColor(255, 255, 255)
            bg_color = QColor(0, 0, 0, 160)  # sfondo semi-trasparente
            
            # Calcola il rettangolo del testo
            text_rect = painter.boundingRect(0, 0, 200, 40, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, zoom_text)
            text_rect.moveTo(text_margin, text_margin)
            # Disegna rettangolo di sfondo e poi il testo
            painter.fillRect(text_rect, bg_color)
            painter.setPen(text_color)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, zoom_text)

            if self.offset_enabled:
                center_x += int(self.center_offset[0] * self.zoom_factor)
                center_y += int(self.center_offset[1] * self.zoom_factor)

            # Disegna cerchi
            for circle in self.circles:
                if circle['visible']:
                    pen = QPen(circle['color'])
                    pen.setWidthF(circle['thickness'] * self.zoom_factor)  # Zoom sullo spessore
                    painter.setPen(pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)

                    scaled_radius = circle['radius'] * self.zoom_factor  # Zoom sul raggio
                    painter.drawEllipse(QPoint(center_x, center_y), int(scaled_radius), int(scaled_radius))

            # Disegna croce solo se visibile
            if self.cross['visible']:
                pen = QPen(self.cross['color'])
                pen.setWidthF(self.cross['thickness'] * self.zoom_factor)  # Zoom sullo spessore
                painter.setPen(pen)

                length = self.cross['length'] * self.zoom_factor  # Zoom sulla lunghezza
                angle_rad = math.radians(self.cross['angle'])

                # Calcola coordinate linee croce ruotate
                x1 = -length * math.cos(angle_rad)
                y1 = -length * math.sin(angle_rad)
                x2 = length * math.cos(angle_rad)
                y2 = length * math.sin(angle_rad)

                x3 = -length * math.cos(angle_rad + math.pi / 2)
                y3 = -length * math.sin(angle_rad + math.pi / 2)
                x4 = length * math.cos(angle_rad + math.pi / 2)
                y4 = length * math.sin(angle_rad + math.pi / 2)

                painter.drawLine(int(center_x + x1), int(center_y + y1), int(center_x + x2), int(center_y + y2))
                painter.drawLine(int(center_x + x3), int(center_y + y3), int(center_x + x4), int(center_y + y4))
        else:
            painter.fillRect(self.rect(), QColor(0, 0, 0))

    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()

        # Fattore di zoom più fine (es. 1.02 è più graduale di 1.1)
        zoom_step = 1.02

        # Conta di quante "tacche" si è mossa la rotella (ogni 120 è una tacca)
        num_steps = delta / 120

        if num_steps > 0:
            self.zoom_factor *= zoom_step ** num_steps  # Zoom in
        else:
            self.zoom_factor /= zoom_step ** abs(num_steps)  # Zoom out

        self.zoom_factor = max(0.39, min(self.zoom_factor, 10.0))  # Range di zoom

        self.update()
    
    # Nuovi setter per la croce
    def set_cross_property(self, prop, value):

        if prop in self.cross:
            self.cross[prop] = value
            print(f"set_cross_property chiamato con {prop}={value}")
            self.update()


    # Metodi pubblici richiesti

    def set_center_offset(self, x, y):
        """Imposta l’offset di spostamento overlay."""
        self.center_offset = (x, y)
        print(f"set_center_offset chiamato con x={x}, y={y}")
        self.update()

    def set_offset_enabled(self, enabled: bool):
        """Abilita o disabilita l’applicazione dell’offset."""
        self.offset_enabled = enabled
        self.update()

    def set_circle_property(self, index, prop, value):
        """Imposta una proprietà di un cerchio (radius, thickness, visible, color)."""
        if 0 <= index < len(self.circles):
            if prop in self.circles[index]:
                self.circles[index][prop] = value
                self.update()

    def update_circle(self, index, radius=None, color=None, thickness=None, visible=None):
        """Aggiorna le proprietà di un cerchio specifico (chiamata da MainWindow)."""
        if 0 <= index < len(self.circles):
            if radius is not None:
                self.circles[index]['radius'] = radius
            if color is not None:
                self.circles[index]['color'] = color
            if thickness is not None:
                self.circles[index]['thickness'] = thickness
            if visible is not None:
                self.circles[index]['visible'] = visible
            self.update()

    def set_center_focus(self, x, y):
        """Imposta il centro di messa a fuoco."""
        self.center_focus = (x, y)
        self.update()
