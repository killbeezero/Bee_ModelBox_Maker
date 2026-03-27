import sys
from PIL import Image

img = Image.open("assets/icon.jpg")

# Windows icon (.ico)
img.save("assets/icon.ico", format="ICO", sizes=[(256, 256)])

# macOS icon (.icns) requires multiple sizes ideally, but for now we'll just save a png
img.save("assets/icon.png", format="PNG")
