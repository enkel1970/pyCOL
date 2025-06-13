import math, os
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QIcon
from PyQt6.QtCore import Qt, QPointF, QLineF

import cv2
import numpy as np


class VideoWindow(QWidget):
    def __init__(self):
        super().__init__()

        # set background color to black
        self.setStyleSheet("background-color: black;")

        # Set the window size and position
        # NOTE: The position is not allowed in wayland protocol.
        # Using wayland this window will be centered and can cover the main window. Use X11 session as workaround.
        self.setGeometry(0, 0, 1280, 960)

        # set minimum size of widget
        # This is useful to avoid resizing too small
        self.setMinimumSize(1280, 960)

        # set window title and icon
        icon_path = os.path.join(os.path.dirname(__file__), "asset", "icon.png")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Collimator Video Overlay")

        # Initialize the video frame.
        self.frame = None
        self.zoom_factor = 0.39  # zoom base

        # Overlay properties for 3 circles (default)
        self.circles = [
            {
                "radius": 500,
                "thickness": 2,
                "visible": False,
                "color": QColor(255, 0, 0),
            },  # Circle 1 red
            {
                "radius": 250,
                "thickness": 2,
                "visible": False,
                "color": QColor(0, 255, 0),
            },  # Circle 2 green
            {
                "radius": 100,
                "thickness": 2,
                "visible": False,
                "color": QColor(0, 0, 255),
            },  # Circle 3 blue
        ]

        # Cross property overlay (default)
        self.cross = {
            "visible": False,
            "length": 100,  # axis length in pixels
            "thickness": 2,  # line thickness in pixels
            "angle": 0,  # angle in degrees
            "color": QColor(85, 0, 127),  # defalt purple color
        }

        # Centro di taratura dal file Ocal (x,y) in pixel, inizialmente angolo in alto a sinistra
        self.center_focus = (0.0, 0.0)

        # Overlay offset (x,y)
        self.center_offset = (0, 0)
        self.offset_enabled = False

    def set_frame(self, frame):
        # Update the video frame
        self.frame = frame
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)

        # Set anti-aliasing and smooth pixmap transform for better quality
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        if self.frame is not None:
            rgb_image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qimg = QImage(
                rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
            )

            scaled_width = int(self.zoom_factor * w)
            scaled_height = int(self.zoom_factor * h)
            pixmap = QPixmap.fromImage(qimg).scaled(
                scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio
            )
            pixmap_x = (self.width() - pixmap.width()) // 2
            pixmap_y = (self.height() - pixmap.height()) // 2

            painter.drawPixmap(pixmap_x, pixmap_y, pixmap)

            # Calcolo corretto del centro in base a center_focus
            center_x = pixmap_x + self.center_focus[0] * self.zoom_factor
            center_y = pixmap_y + self.center_focus[1] * self.zoom_factor

            # Disegna lo zoom factor in alto a sinistra
            zoom_text = f"Zoom: {self.zoom_factor:.2f}x"
            font = painter.font()
            font.setPointSize(14)
            painter.setFont(font)

            text_margin = 10
            text_color = QColor(255, 255, 255)
            bg_color = QColor(0, 0, 0, 160)  # sfondo semi-trasparente

            # Calcola il rettangolo del testo
            text_rect = painter.boundingRect(
                0,
                0,
                200,
                40,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                zoom_text,
            )
            text_rect.moveTo(text_margin, text_margin)
            # Disegna rettangolo di sfondo e poi il testo
            painter.fillRect(text_rect, bg_color)
            painter.setPen(text_color)
            painter.drawText(
                text_rect,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                zoom_text,
            )

            if self.offset_enabled:
                center_x += self.center_offset[0] * self.zoom_factor
                center_y += self.center_offset[1] * self.zoom_factor

            # Disegna cerchi
            for circle in self.circles:
                if circle["visible"]:
                    pen = QPen(circle["color"])
                    pen.setWidthF(
                        circle["thickness"] * self.zoom_factor
                    )  # Zoom sullo spessore
                    painter.setPen(pen)
                    painter.setBrush(Qt.BrushStyle.NoBrush)

                    scaled_radius = (
                        circle["radius"] * self.zoom_factor
                    )  # Zoom sul raggio
                    painter.drawEllipse(
                        QPointF(center_x, center_y), scaled_radius, scaled_radius
                    )

            # Disegna croce solo se visibile
            if self.cross["visible"]:
                pen = QPen(self.cross["color"])
                pen.setWidthF(
                    self.cross["thickness"] * self.zoom_factor
                )  # Zoom sullo spessore
                painter.setPen(pen)

                length = self.cross["length"] * self.zoom_factor  # Zoom sulla lunghezza
                angle_rad = math.radians(self.cross["angle"])

                # Calcola coordinate linee croce ruotate
                x1 = -length * math.cos(angle_rad)
                y1 = -length * math.sin(angle_rad)
                x2 = length * math.cos(angle_rad)
                y2 = length * math.sin(angle_rad)

                x3 = -length * math.cos(angle_rad + math.pi / 2)
                y3 = -length * math.sin(angle_rad + math.pi / 2)
                x4 = length * math.cos(angle_rad + math.pi / 2)
                y4 = length * math.sin(angle_rad + math.pi / 2)

                v_line = QLineF(
                    center_x + x1, center_y + y1, center_x + x2, center_y + y2
                )
                h_line = QLineF(
                    center_x + x3, center_y + y3, center_x + x4, center_y + y4
                )

                painter.drawLine(v_line)
                painter.drawLine(h_line)
        else:
            painter.fillRect(self.rect(), QColor(0, 0, 0))

    # Zoom can be done with the mouse wheel
    # This method is called when the mouse wheel is scrolled
    # The zoom factor is adjusted based on the scroll direction and amount
    # The zoom factor is a multiplicative factor that scales the image size
    # The zoom factor is clamped to a range to prevent excessive zooming in or out
    def wheelEvent(self, event):
        delta = event.angleDelta().y()

        # Fine zoom factor (es. 1.02 is more fine than 1.1)
        zoom_step = 1.02

        # count the tick of mouse wheel (120 tick = 1 step)
        # If the wheel is scrolled up, delta is positive, if down, delta is negative
        num_steps = delta / 120

        if num_steps > 0:
            self.zoom_factor *= zoom_step**num_steps  # Zoom in
        else:
            self.zoom_factor /= zoom_step ** abs(num_steps)  # Zoom out

        self.zoom_factor = max(0.39, min(self.zoom_factor, 10.0))  # Range di zoom

        self.update()

    # method to seet cross properties
    def set_cross_property(self, prop, value):
        if prop in self.cross:
            self.cross[prop] = value
            self.update()

    # Public methods to set properties of the overlay

    # Set the overlay center offset (x, y) in pixels.
    def set_center_offset(self, x, y):
        self.center_offset = (x, y * -1)  # Invert y-axis for correct display up/down
        self.update()

    # Set the visibility of the cross overlay.
    def set_offset_enabled(self, enabled: bool):
        # Enable or disable the offset feature.
        self.offset_enabled = enabled
        self.update()

    # Set a property of a specific circle by index.
    # index: index of the circle (0, 1, 2)
    # prop: property name (e.g., 'radius', 'color', 'thickness', 'visible')
    # value: new value for the property
    def set_circle_property(self, index, prop, value):

        if 0 <= index < len(self.circles):

            if prop in self.circles[index]:
                self.circles[index][prop] = value
                self.update()

    # Update circle properties by index
    def update_circle(
        self, index, radius=None, color=None, thickness=None, visible=None
    ):

        if 0 <= index < len(self.circles):
            if radius is not None:
                self.circles[index]["radius"] = radius
            if color is not None:
                self.circles[index]["color"] = color
            if thickness is not None:
                self.circles[index]["thickness"] = thickness
            if visible is not None:
                self.circles[index]["visible"] = visible
            self.update()

    # Set the center of focus for the overlay.
    def set_center_focus(self, x, y):
        self.center_focus = (x, y)
        self.update()
