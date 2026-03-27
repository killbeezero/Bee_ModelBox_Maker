import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QFontMetrics, QPainterPath
app = QApplication(sys.argv)
f = QFont("Arial", 210, QFont.Weight.Bold)
fm = QFontMetrics(f)
print("Ascent:", fm.ascent())
print("Descent:", fm.descent())
print("Height:", fm.height())
