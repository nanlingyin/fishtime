# ui/title_bar.py
import os
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont, QPixmap, QPalette
from PyQt5.QtCore import Qt
from utils import circle_button_style

class TitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setAutoFillBackground(True)
        self.setBackgroundRole(QPalette.Window)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.setLayout(self.layout)
        self.setFixedHeight(50)

        # 设置应用图标
        icon_path = r'icon\text.png'
        if os.path.exists(icon_path):
            self.icon_label = QLabel()
            pixmap = QPixmap(icon_path).scaled(30, 30, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.icon_label.setPixmap(pixmap)
            self.layout.addWidget(self.icon_label)
        else:
            self.icon_label = QLabel()
            self.layout.addWidget(self.icon_label)

        # 设置标题
        self.title = QLabel("摸鱼时间记录" if self.parent.current_language == "zh_CN" else "Time Tracker")
        self.title.setFont(QFont(self.parent.config.get("font_family", "Microsoft YaHei"), 16))
        self.layout.addWidget(self.title)

        self.layout.addStretch()

        # 窗口控制按钮
        button_size = 35

        self.min_button = QPushButton("")
        self.min_button.setFixedSize(button_size, button_size)
        self.min_button.setStyleSheet(circle_button_style("#FFBD44"))
        self.min_button.setToolTip("最小化" if self.parent.current_language == "zh_CN" else "Minimize")
        self.min_button.clicked.connect(self.parent.showMinimized)
        self.min_button.setCursor(Qt.PointingHandCursor)
        self.layout.addWidget(self.min_button)

        self.max_button = QPushButton("")
        self.max_button.setFixedSize(button_size, button_size)
        self.max_button.setStyleSheet(circle_button_style("#5A67D8"))
        self.max_button.setToolTip("最大化" if self.parent.current_language == "zh_CN" else "Maximize")
        self.max_button.clicked.connect(self.toggle_maximize)
        self.max_button.setCursor(Qt.PointingHandCursor)
        self.layout.addWidget(self.max_button)

        self.close_button = QPushButton("")
        self.close_button.setFixedSize(button_size, button_size)
        self.close_button.setStyleSheet(circle_button_style("#E53E3E"))
        self.close_button.setToolTip("关闭" if self.parent.current_language == "zh_CN" else "Close")
        self.close_button.clicked.connect(self.parent.close)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.layout.addWidget(self.close_button)

        self.start = None

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
            self.max_button.setText("")
            self.max_button.setStyleSheet(circle_button_style("#5A67D8"))
            self.max_button.setToolTip("最大化" if self.parent.current_language == "zh_CN" else "Maximize")
        else:
            self.parent.showMaximized()
            self.max_button.setText("")
            self.max_button.setStyleSheet(circle_button_style("#63B3ED"))
            self.max_button.setToolTip("还原" if self.parent.current_language == "zh_CN" else "Restore")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start = event.globalPos()
            self.click_position = event.pos()

    def mouseMoveEvent(self, event):
        if self.start:
            delta = event.globalPos() - self.start
            self.parent.move(self.parent.pos() + delta)
            self.start = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.start = None

    def update_ui_texts(self, language):
        """更新UI文本"""
        self.title.setText("摸鱼时间记录" if language == "zh_CN" else "Time Tracker")
        self.min_button.setToolTip("最小化" if language == "zh_CN" else "Minimize")
        if self.parent.isMaximized():
            self.max_button.setToolTip("还原" if language == "zh_CN" else "Restore")
        else:
            self.max_button.setToolTip("最大化" if language == "zh_CN" else "Maximize")
        self.close_button.setToolTip("关闭" if language == "zh_CN" else "Close")