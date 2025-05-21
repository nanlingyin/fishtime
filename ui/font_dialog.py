# ui/font_dialog.py
from PyQt5.QtWidgets import QDialog, QFormLayout, QPushButton, QDialogButtonBox, QFontDialog, QColorDialog
from PyQt5.QtGui import QColor

class FontSettingsDialog(QDialog):
    def __init__(self, current_font, current_color, language, parent=None):
        super().__init__(parent)
        self.setWindowTitle("字体设置" if language == "zh_CN" else "Font Settings")
        self.setFixedSize(500, 300)
        self.selected_font = current_font
        self.selected_color = QColor(current_color)
        self.language = language

        self.layout = QFormLayout()
        self.setLayout(self.layout)

        # 字体选择
        self.font_button = QPushButton("选择字体" if language == "zh_CN" else "Choose Font")
        self.font_button.clicked.connect(self.choose_font)
        self.layout.addRow("字体:" if language == "zh_CN" else "Font:", self.font_button)

        # 字体颜色选择
        self.color_button = QPushButton("选择颜色" if language == "zh_CN" else "Choose Color")
        self.color_button.clicked.connect(self.choose_color)
        self.layout.addRow("字体颜色:" if language == "zh_CN" else "Font Color:", self.color_button)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def choose_font(self):
        dialog = QFontDialog(self)
        dialog.setOption(QFontDialog.DontUseNativeDialog, True)
        dialog.setCurrentFont(self.selected_font)
        dialog.setWindowTitle("选择字体" if self.language == "zh_CN" else "Choose Font")
        if dialog.exec_() == QDialog.Accepted:
            self.selected_font = dialog.selectedFont()

    def choose_color(self):
        dialog_title = "选择字体颜色" if self.language == "zh_CN" else "Choose Font Color"
        color = QColorDialog.getColor(self.selected_color, self, dialog_title)
        if color.isValid():
            self.selected_color = color

    def get_settings(self):
        return self.selected_font, self.selected_color.name()