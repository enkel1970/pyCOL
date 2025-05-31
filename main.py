import sys, os
from PyQt6.QtWidgets import QApplication
from PyQt6 import uic
from mainwindow import MainWindow
from PyQt6.QtGui import QIcon

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Normalizza il percorso del file .ui
    ui_file_path = os.path.join(os.path.dirname(__file__), 'ui', 'mainwindow.ui')
    asset_file_path = os.path.join(os.path.dirname(__file__), 'asset', 'icon.png')
        
    # Carica l'interfaccia utente
    ui = uic.loadUi(ui_file_path)

    print(asset_file_path)
    
    icon = QIcon (asset_file_path)
    size = QApplication.primaryScreen().size()
    
    window = MainWindow(ui)
    ui.window().setGeometry(size.width() - 363, 0, 363, 919)
    ui.show()
    

    ui.window().setWindowTitle("OCAL 2 Collimator for Linux")
    ui.window().setWindowIcon(icon)
    
    sys.exit(app.exec())

