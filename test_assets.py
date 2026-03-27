import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys, '_MEIPASS'):
    ASSETS_DIR = os.path.join(sys._MEIPASS, "assets")
else:
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")

label_path = os.path.join(ASSETS_DIR, "label.png")
print("ASSETS_DIR:", ASSETS_DIR)
print("label_path:", label_path)
print("label_path exists?", os.path.exists(label_path))

try:
    from PyQt6.QtGui import QPixmap
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    pixmap = QPixmap(label_path)
    print("Pixmap loaded successfully, is null?", pixmap.isNull())
except Exception as e:
    print("Error loading pixmap:", e)
