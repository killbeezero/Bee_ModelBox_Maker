import sys
import os
import requests
import json
import subprocess
from io import BytesIO
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLineEdit, QPushButton, QListWidget, QGraphicsView, QGraphicsScene, 
                             QGraphicsPixmapItem, QMessageBox, QLabel, QListWidgetItem, QGraphicsPathItem, 
                             QSizePolicy, QGraphicsRectItem, QDialog, QFormLayout)
from PyQt6.QtGui import QPixmap, QImage, QPainter, QFont, QColor, QPen, QPainterPath, QIcon, QFontDatabase, QTransform, QBrush, QFontMetrics
from PyQt6.QtCore import Qt, QSize, QPointF

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if hasattr(sys, '_MEIPASS'):
    ASSETS_DIR = os.path.join(sys._MEIPASS, "assets")
else:
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CONFIG_FILE = os.path.expanduser("~/.Bee_ModelBox_Config.json")
CANVAS_WIDTH = 1583
CANVAS_HEIGHT = 661

class SettingsDialog(QDialog):
    def __init__(self, current_key, parent=None):
        super().__init__(parent)
        self.setWindowTitle("設定")
        self.setMinimumWidth(600)  # 增加寬度
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.api_key_input = QLineEdit(current_key)
        self.api_key_input.setPlaceholderText("在此輸入 Serper.dev API Key")
        self.api_key_input.setMinimumWidth(450)  # 增加輸入框寬度
        form.addRow("Serper API Key:", self.api_key_input)
        
        layout.addLayout(form)
        
        btns = QHBoxLayout()
        save_btn = QPushButton("儲存")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def get_key(self):
        return self.api_key_input.text().strip()

class EnhancedGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

class ModelBoxLabelMaker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bee ModelBox Maker 1.0 (懸浮尺寸版) 🦞")
        self.resize(1450, 850); self.image_urls = []
        self.current_page_idx = 1
        self.api_key = ""
        
        self.iori_id = QFontDatabase.addApplicationFont(os.path.join(ASSETS_DIR, "Iori.otf"))
        self.iori_font = QFontDatabase.applicationFontFamilies(self.iori_id)[0] if self.iori_id != -1 else "Arial"
        self.chiron_id = QFontDatabase.addApplicationFont(os.path.join(ASSETS_DIR, "ChironHeiHK-B.otf"))
        self.chiron_font = QFontDatabase.applicationFontFamilies(self.chiron_id)[0] if self.chiron_id != -1 else "Arial"

        self.init_ui(); self.load_saved_key()
        QApplication.processEvents(); self.update_view_scale(); self.update_preview_text()

    def init_ui(self):
        ml = QHBoxLayout(); lp = QVBoxLayout()
        
        # 頂部控制欄：隱藏 API 欄位，改用設定按鈕
        top_ctl = QHBoxLayout()
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setToolTip("設定 API Key")
        self.settings_btn.clicked.connect(self.open_settings)
        top_ctl.addWidget(QLabel("1. 資訊輸入"))
        top_ctl.addStretch()
        top_ctl.addWidget(self.settings_btn)
        
        self.series_input = QLineEdit("RG"); self.model_input = QLineEdit("RX-78-2")
        self.series_input.textChanged.connect(self.update_preview_text); self.model_input.textChanged.connect(self.update_preview_text)
        
        s_ctl = QHBoxLayout()
        sb = QPushButton("🔍 搜尋"); sb.clicked.connect(self.start_new_search)
        mb = QPushButton("➕ More"); mb.clicked.connect(self.load_next_page)
        cb = QPushButton("🗑️ 清空"); cb.clicked.connect(self.clear_results)
        s_ctl.addWidget(sb); s_ctl.addWidget(mb); s_ctl.addWidget(cb)
        
        self.results_list = QListWidget(); self.results_list.setViewMode(QListWidget.ViewMode.IconMode); self.results_list.setIconSize(QSize(100, 100)); self.results_list.setSpacing(5); self.results_list.itemClicked.connect(self.load_selected_image)
        svb = QPushButton("💾 輸出標籤至 Downloads"); svb.clicked.connect(self.save_result); svb.setStyleSheet("background-color: #2ecc71; color: white; padding: 15px; font-weight: bold;")
        
        lp.addLayout(top_ctl)
        lp.addWidget(self.series_input); lp.addWidget(self.model_input); lp.addLayout(s_ctl)
        lp.addWidget(QLabel("2. 選擇圖塊 (懸浮看解析度)")); lp.addWidget(self.results_list); lp.addWidget(svb)
        
        self.scene = QGraphicsScene(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT); self.view = EnhancedGraphicsView(self.scene); self.view.setRenderHint(QPainter.RenderHint.Antialiasing); self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform); self.view.setStyleSheet("background-color: #111111; border: none;"); self.view.viewport().installEventFilter(self)
        self.white_bg = QGraphicsRectItem(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT); self.white_bg.setBrush(QBrush(Qt.GlobalColor.white)); self.white_bg.setPen(QPen(Qt.GlobalColor.transparent)); self.scene.addItem(self.white_bg); self.white_bg.setZValue(-5)
        self.img_item = QGraphicsPixmapItem(); self.img_item.setFlag(QGraphicsPixmapItem.GraphicsItemFlag.ItemIsMovable); self.scene.addItem(self.img_item); self.img_item.setZValue(0)
        self.frame_item = QGraphicsPixmapItem(); f_p = os.path.join(ASSETS_DIR, "label.png")
        if os.path.exists(f_p): self.frame_item.setPixmap(QPixmap(f_p))
        self.scene.addItem(self.frame_item); self.frame_item.setZValue(10)
        self.series_text_item = QGraphicsPathItem(); self.model_text_item = QGraphicsPathItem()
        self.scene.addItem(self.series_text_item); self.scene.addItem(self.model_text_item)
        self.series_text_item.setZValue(20); self.model_text_item.setZValue(20)
        
        ml.addLayout(lp, 1); ml.addWidget(self.view, 4); cw = QWidget(); cw.setLayout(ml); self.setCentralWidget(cw)

    def open_settings(self):
        diag = SettingsDialog(self.api_key, self)
        if diag.exec():
            self.api_key = diag.get_key()
            json.dump({"api_key": self.api_key}, open(CONFIG_FILE, "w"))
            QMessageBox.information(self, "成功", "API Key 已儲存")

    def start_new_search(self): self.clear_results(); self.current_page_idx = 1; self.search_images()
    def load_next_page(self): self.current_page_idx += 1; self.search_images()
    def clear_results(self): self.results_list.clear(); self.image_urls = []

    def eventFilter(self, source, event):
        if event.type() == event.Type.Wheel and source is self.view.viewport():
            dy = event.angleDelta().y(); z = 1.05 if dy > 0 else 0.95
            if not self.img_item.pixmap().isNull():
                r = self.img_item.pixmap().rect(); self.img_item.setTransformOriginPoint(QPointF(r.width()/2, r.height()/2))
                self.img_item.setScale(self.img_item.scale() * z)
            return True
        return super().eventFilter(source, event)

    def update_view_scale(self):
        sc = (self.view.width() - 30) / CANVAS_WIDTH
        self.view.setTransform(QTransform().scale(sc, sc))

    def resizeEvent(self, event): self.update_view_scale(); super().resizeEvent(event)

    def update_preview_text(self):
        def mk_path(txt, ff, s, x, y):
            p = QPainterPath(); f = QFont(ff, s, QFont.Weight.Bold); p.addText(x, y, f, txt); return p
        # y 軸在 QGraphicsTextItem 的 QPainterPath 比較容易掌握，直接寫死為 180 (大約符合字體大小的基線)
        self.series_text_item.setPath(mk_path(self.series_input.text(), self.iori_font, 210, 40, 180))
        self.series_text_item.setPen(QPen(Qt.GlobalColor.white, 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        self.series_text_item.setBrush(Qt.GlobalColor.black)
        self.model_text_item.setPath(mk_path(self.model_input.text(), self.chiron_font, 70, 50, CANVAS_HEIGHT - 50))
        self.model_text_item.setPen(QPen(QColor("#333333"), 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        self.model_text_item.setBrush(Qt.GlobalColor.white)

    def load_saved_key(self):
        if os.path.exists(CONFIG_FILE):
            try: self.api_key = json.load(open(CONFIG_FILE)).get("api_key", "")
            except: pass

    def search_images(self):
        q = f"{self.series_input.text()} {self.model_input.text()} boxart large"; ak = self.api_key.strip()
        if not ak:
            QMessageBox.warning(self, "警告", "請先點選齒輪設定 API Key")
            return
        url = "https://google.serper.dev/images"
        try:
            res = requests.post(url, headers={'X-API-KEY': ak, 'Content-Type': 'application/json'}, data=json.dumps({"q": q, "num": 10, "page": self.current_page_idx}))
            rj = res.json().get('images', [])
            for px in rj:
                self.image_urls.append(px['imageUrl'])
                pix = QPixmap(); pix.loadFromData(requests.get(px['thumbnailUrl'], timeout=5).content)
                item = QListWidgetItem(QIcon(pix), "")
                item.setToolTip(f"解析度: {px.get('width', 'N/A')} x {px.get('height', 'N/A')}\n來源: {px.get('source', '未知')}")
                self.results_list.addItem(item)
        except Exception as e: QMessageBox.critical(self, "失敗", str(e))

    def load_selected_image(self, item):
        idx = self.results_list.row(item)
        try:
            res = requests.get(self.image_urls[idx], headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            pix = QPixmap(); pix.loadFromData(res.content)
            self.img_item.setPixmap(pix); self.img_item.setOffset(0, 0); self.img_item.setScale(0.5)
            r = pix.rect(); self.img_item.setTransformOriginPoint(QPointF(r.width()/2, r.height()/2))
            self.img_item.setPos((CANVAS_WIDTH/2)-(r.width()/2), (CANVAS_HEIGHT/2)-(r.height()/2))
        except: QMessageBox.warning(self, "警告", "載入失敗")

    def save_result(self):
        final = QImage(CANVAS_WIDTH, CANVAS_HEIGHT, QImage.Format.Format_ARGB32); final.fill(Qt.GlobalColor.white)
        p = QPainter(final); p.setRenderHint(QPainter.RenderHint.Antialiasing); p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        if not self.img_item.pixmap().isNull():
            p.save(); pix = self.img_item.pixmap(); rect = pix.rect()
            p.translate(self.img_item.pos() + QPointF(rect.width()/2, rect.height()/2)); p.scale(self.img_item.scale(), self.img_item.scale())
            p.translate(-QPointF(rect.width()/2, rect.height()/2)); p.drawPixmap(0, 0, pix); p.restore()
        if not self.frame_item.pixmap().isNull(): p.drawPixmap(0, 0, self.frame_item.pixmap())
        def dr_f(pt, tx, ff, sz, x, y, c_o, c_f, sw):
            ph = QPainterPath(); fn = QFont(ff, sz, QFont.Weight.Bold); pt.setFont(fn); y_real = y if y != 0 else 180
            ph.addText(x, y_real, fn, tx); pt.setPen(QPen(c_o, sw, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            pt.drawPath(ph); pt.fillPath(ph, c_f)
        dr_f(p, self.series_input.text(), self.iori_font, 210, 40, 0, Qt.GlobalColor.white, Qt.GlobalColor.black, 7)
        dr_f(p, self.model_input.text(), self.chiron_font, 70, 50, CANVAS_HEIGHT - 50, QColor("#333333"), Qt.GlobalColor.white, 3)
        p.end(); path = os.path.expanduser("~/Downloads/model_label.png"); final.save(path); QMessageBox.information(self, "完成", f"存至 Downloads 🦞")

if __name__ == "__main__":
    app = QApplication(sys.argv); window = ModelBoxLabelMaker(); window.show(); sys.exit(app.exec())
