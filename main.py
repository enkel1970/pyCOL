# -*- coding: utf-8 -*-
'''
Author: Carlo Moisè 
email: carlo.moise@libero.it
Version: 0.0.1
Date: 2025-06-02

This software is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or (at your option)
any later version.

This software is distributed in the hope that it will be useful,
but **WITHOUT ANY WARRANTY**; without even the implied warranty of
**MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE**. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.

────────────────────────────────────────────────────────────────────────

**DISCLAIMER OF LIABILITY**

This software is provided "as is", without any express or implied warranties.
The author shall not be held liable for any direct, indirect, incidental, special
or consequential damages arising out of the use or inability to use this software,
including but not limited to loss of data, business interruption, hardware or
software malfunction, or any other financial losses.

You use this software **at your own risk**. It is your responsibility to
verify the compatibility, safety, and reliability of the software in any
operational context.

────────────────────────────────────────────────────────────────────────
'''

import sys, os
from PyQt6.QtWidgets import QApplication
from PyQt6 import uic
from mainwindow import MainWindow
from PyQt6.QtGui import QIcon

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Normalize the path to the UI and asset files 
    ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'mainwindow.ui')
    asset_file_path = os.path.join(os.path.dirname(__file__), 'asset', 'icon.png')
        
    # Load the UI file
    ui = uic.loadUi(ui_file_path)
    
    icon = QIcon (asset_file_path)
    size = QApplication.primaryScreen().size()
    
    window = MainWindow(ui)

    # Set the main window to the UI position and size
    # NOTE: The position is not allowed in wayland protocol!
    ui.window().setGeometry(size.width() - 363, 0, 363, 750)
    ui.show()
    ui.window().setWindowTitle("Python Newtonian Telescope Collimator")
    ui.window().setWindowIcon(icon)
    
    sys.exit(app.exec())

