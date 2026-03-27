import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont, QImage, QPainter, QPainterPath

app = QApplication(sys.argv)

f_pt = QFont("Arial", 210)
f_px = QFont("Arial")
f_px.setPixelSize(210)

print(f"Point Size 210 -> Pixel Size: {f_pt.pixelSize()} (may be -1 if not set explicitly, point size: {f_pt.pointSize()})")
print(f"Pixel Size 210 -> Pixel Size: {f_px.pixelSize()} (point size: {f_px.pointSize()})")

img = QImage(1000, 1000, QImage.Format.Format_ARGB32)
p = QPainter(img)
p.setFont(f_pt)
print("Font metrics on QImage with point size 210, height:", p.fontMetrics().height())
p.setFont(f_px)
print("Font metrics on QImage with pixel size 210, height:", p.fontMetrics().height())
p.end()

