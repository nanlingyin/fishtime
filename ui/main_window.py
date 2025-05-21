# ui/main_window.py
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSystemTrayIcon, QMenu, QAction, QMessageBox, QGroupBox, QListWidget,
    QComboBox, QInputDialog, QListWidgetItem, QDialog, QCheckBox
)
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QFont

from ui.title_bar import TitleBar
from ui.font_dialog import FontSettingsDialog
from ui.report import generate_report, show_chart
from process_monitor import get_active_window, get_process_icon
from config import load_config, save_config
from constants import LANGUAGES, IGNORE_LIST, THEMES
from db import init_db, log_usage, clear_records, get_total_usage_time, get_tracked_processes
from utils import format_duration

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.current_language = self.config.get("language", "zh_CN")
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(THEMES[self.config.get("theme", "灰色")].format(
            font_family=self.config.get("font_family", "Microsoft YaHei"),
            font_color=self.config.get("font_color", "#2E3440")
        ))

        self.title_bar = TitleBar(self)
        self.setCentralWidget(QWidget())
        self.main_layout = QVBoxLayout()
        self.centralWidget().setLayout(self.main_layout)
        self.main_layout.addWidget(self.title_bar)

        # 添加内容区域
        self.content = QWidget()
        self.content_layout = QVBoxLayout()
        self.content.setLayout(self.content_layout)
        self.main_layout.addWidget(self.content)

        # 总摸鱼时长标签
        self.total_time_label = QLabel()
        self.total_time_label.setAlignment(Qt.AlignCenter)
        self.total_time_label.setFont(QFont(self.config.get("font_family", "Microsoft YaHei"), 14))
        self.content_layout.addWidget(self.total_time_label)

        # 当前应用名称和图标
        self.current_app_label = QLabel(LANGUAGES[self.current_language]["current_app"].format("无"))
        self.current_app_label.setAlignment(Qt.AlignCenter)
        self.current_app_label.setFont(QFont(self.config.get("font_family", "Microsoft YaHei"), 14))
        self.content_layout.addWidget(self.current_app_label)

        self.current_icon_label = QLabel()
        default_pixmap = QPixmap(64, 64)
        default_pixmap.fill(Qt.gray)
        self.current_icon_label.setPixmap(default_pixmap)
        self.current_icon_label.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(self.current_icon_label)

        # 跟踪控制按钮
        self.toggle_tracking_button = QPushButton(LANGUAGES[self.current_language]["start_tracking"])
        self.toggle_tracking_button.clicked.connect(self.toggle_tracking)
        self.content_layout.addWidget(self.toggle_tracking_button)

        # 生成报告按钮
        self.report_button = QPushButton(LANGUAGES[self.current_language]["report"])
        self.report_button.clicked.connect(lambda: generate_report(self.current_language))
        self.content_layout.addWidget(self.report_button)

        # 清除记录按钮
        self.clear_button = QPushButton(LANGUAGES[self.current_language]["clear"])
        self.clear_button.clicked.connect(self.clear_records_confirmation)
        self.content_layout.addWidget(self.clear_button)

        # 字体设置按钮
        self.font_settings_button = QPushButton(LANGUAGES[self.current_language]["font_settings"])
        self.font_settings_button.clicked.connect(self.open_font_settings)
        self.content_layout.addWidget(self.font_settings_button)

        # 语言选择
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文", "English"])
        self.language_combo.setCurrentIndex(0 if self.current_language == "zh_CN" else 1)
        self.language_combo.currentIndexChanged.connect(self.change_language)
        self.content_layout.addWidget(self.language_combo)

        # 主题选择
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["暗黑", "白色", "灰色"])
        self.theme_combo.setCurrentText(self.config.get("theme", "灰色"))
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        self.content_layout.addWidget(self.theme_combo)

        # 进程白名单管理
        self.whitelist_group = QGroupBox(LANGUAGES[self.current_language]["process_whitelist"])
        self.whitelist_layout = QVBoxLayout()
        self.whitelist_group.setLayout(self.whitelist_layout)
        self.content_layout.addWidget(self.whitelist_group)

        self.whitelist_list = QListWidget()
        self.whitelist_layout.addWidget(self.whitelist_list)

        # 添加白名单按钮布局
        self.whitelist_buttons_layout = self.create_whitelist_buttons_layout()
        self.whitelist_layout.addLayout(self.whitelist_buttons_layout)

        # 系统托盘
        self.create_tray_icon()

        # 跟踪定时器
        self.tracking_timer = QTimer()
        self.tracking_timer.timeout.connect(self.track_usage)
        self.tracking = False
        self.duration = 0

        # 更新当前应用显示
        self.update_current_app()
        # 加载白名单
        self.load_whitelist()
        # 定时更新当前应用
        self.app_update_timer = QTimer()
        self.app_update_timer.timeout.connect(self.update_current_app)
        self.app_update_timer.start(1000)  # 每秒更新一次
        # 初始化计时器
        self.init_total_time_timer()

        # 更新总摸鱼时长
        self.update_total_time()

    def load_whitelist(self):
        whitelist = self.config.get("Process Whitelist", [])
        for process in whitelist:
            self.whitelist_list.addItem(process)
            # 确保进程在忽略列表中
            if process not in IGNORE_LIST:
                IGNORE_LIST.append(process)

    def add_to_whitelist(self):
        text, ok = QInputDialog.getText(
            self,
            LANGUAGES[self.current_language]["add_process"],
            LANGUAGES[self.current_language]["add_process"]
        )
        if ok and text:
            if text not in IGNORE_LIST:
                self.whitelist_list.addItem(text)
                IGNORE_LIST.append(text)
                self.config["Process Whitelist"].append(text)
                save_config(self.config)
            else:
                QMessageBox.warning(
                    self,
                    LANGUAGES[self.current_language]["error"],
                    f"{text} {LANGUAGES[self.current_language].get('already_in_whitelist', '已经在白名单中。')}"
                )

    def remove_from_whitelist(self):
        selected_items = self.whitelist_list.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            process = item.text()
            if process in IGNORE_LIST:
                IGNORE_LIST.remove(process)
            if process in self.config["Process Whitelist"]:
                self.config["Process Whitelist"].remove(process)
            self.whitelist_list.takeItem(self.whitelist_list.row(item))
        save_config(self.config)

    def init_total_time_timer(self):
        self.total_time_timer = QTimer()
        self.total_time_timer.timeout.connect(self.update_total_time)
        self.total_time_timer.start(1000)  # 每秒更新一次

    def update_total_time(self):
        total_seconds = get_total_usage_time()
        formatted_time = format_duration(total_seconds, self.current_language)
        self.total_time_label.setText(LANGUAGES[self.current_language]["fish"]+formatted_time)

    def apply_theme(self):
        self.setStyleSheet(THEMES[self.config.get("theme", "灰色")].format(
            font_family=self.config.get("font_family", "Microsoft YaHei"),
            font_color=self.config.get("font_color", "#2E3440")
        ))
        self.title_bar.title.setFont(QFont(self.config.get("font_family", "Microsoft YaHei"), 16))
        self.update_ui_language()

    def create_tray_icon(self):
        icon_path = r'icon\text.png'
        if os.path.exists(icon_path):
            tray_icon = QIcon(icon_path)
        else:
            tray_icon = QIcon()

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(tray_icon)
        self.tray.setVisible(True)

        menu = QMenu()

        show_action = QAction(LANGUAGES[self.current_language]["tray_show"])
        show_action.triggered.connect(self.show_normal)
        menu.addAction(show_action)

        exit_action = QAction(LANGUAGES[self.current_language]["tray_exit"])
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.tray_icon_clicked)

    def track_usage(self):
        app_name = get_active_window()
        if app_name:
            log_usage(app_name, 1)  # 每秒记录一次
        self.duration += 1

    def closeEvent(self, event):
        # 弹出对话框询问用户是要最小化到托盘还是直接退出
        dialog_buttons = QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
        dialog_title = LANGUAGES[self.current_language].get("close_dialog_title", "关闭确认") if self.current_language == "zh_CN" else "Close Confirmation"
        dialog_text = LANGUAGES[self.current_language].get("close_dialog_text", "您想要将应用最小化到托盘吗？") if self.current_language == "zh_CN" else "Do you want to minimize the application to the system tray?"
        dialog_yes = LANGUAGES[self.current_language].get("close_dialog_yes", "最小化到托盘") if self.current_language == "zh_CN" else "Minimize to Tray"
        dialog_no = LANGUAGES[self.current_language].get("close_dialog_no", "退出应用") if self.current_language == "zh_CN" else "Exit Application"
        dialog_cancel = LANGUAGES[self.current_language].get("close_dialog_cancel", "取消") if self.current_language == "zh_CN" else "Cancel"
        
        # 创建自定义按钮的消息框
        message_box = QMessageBox(self)
        message_box.setWindowTitle(dialog_title)
        message_box.setText(dialog_text)
        message_box.setIcon(QMessageBox.Question)
        
        # 添加自定义按钮文本
        minimize_button = message_box.addButton(dialog_yes, QMessageBox.YesRole)
        exit_button = message_box.addButton(dialog_no, QMessageBox.NoRole)
        cancel_button = message_box.addButton(dialog_cancel, QMessageBox.RejectRole)
        
        message_box.exec_()
        
        clicked_button = message_box.clickedButton()
        
        if clicked_button == minimize_button:
            # 最小化到托盘
            event.ignore()
            self.hide()
            self.tray.setVisible(True)
            self.tray.showMessage(
                LANGUAGES[self.current_language]["information"],
                LANGUAGES[self.current_language]["tray_minimized"],
                QSystemTrayIcon.Information,
                2000
            )
        elif clicked_button == exit_button:
            # 退出应用
            from PyQt5.QtWidgets import QApplication
            self.tray.hide()
            event.accept()
            QApplication.quit()
        else:  # cancel_button or closed dialog
            # 取消关闭
            event.ignore()

    def tray_icon_clicked(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.show_normal()

    def show_normal(self):
        self.show()
        self.tray.hide()

    def exit_app(self):
        from PyQt5.QtWidgets import QApplication
        QApplication.quit()

    def clear_records_confirmation(self):
        reply = QMessageBox.question(self, LANGUAGES[self.current_language]["clear_confirm_title"],
                                    LANGUAGES[self.current_language]["clear_confirm_text"],
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            clear_records()
            QMessageBox.information(self, LANGUAGES[self.current_language]["information"], 
                                   LANGUAGES[self.current_language]["clear_success"])

    def open_font_settings(self):
        dialog = FontSettingsDialog(QFont(self.config.get("font_family", "Microsoft YaHei"), 12),
                                   self.config.get("font_color", "#2E3440"),
                                   self.current_language,
                                   self)
        if dialog.exec_() == QDialog.Accepted:
            selected_font, selected_color = dialog.get_settings()
            self.config["font_family"] = selected_font.family()
            self.config["font_color"] = selected_color
            save_config(self.config)
            self.apply_theme()

    def change_language(self, index):
        self.current_language = "zh_CN" if index == 0 else "en_US"
        self.config["language"] = self.current_language
        save_config(self.config)
        self.apply_theme()
        self.update_whitelist_ui_texts()

    def change_theme(self, index):
        themes = ["暗黑", "白色", "灰色"]
        selected_theme = themes[index]
        self.config["theme"] = selected_theme
        save_config(self.config)
        self.apply_theme()

    def update_ui_language(self):
        self.toggle_tracking_button.setText(
            LANGUAGES[self.current_language]["stop_tracking"] if self.tracking else LANGUAGES[self.current_language]["start_tracking"]
        )
        self.report_button.setText(LANGUAGES[self.current_language]["report"])
        self.clear_button.setText(LANGUAGES[self.current_language]["clear"])
        self.font_settings_button.setText(LANGUAGES[self.current_language]["font_settings"])
        self.language_combo.setItemText(0, "中文" if self.current_language == "zh_CN" else "Chinese")
        self.language_combo.setItemText(1, "English" if self.current_language == "en_US" else "英语")
        self.theme_combo.setItemText(0, "暗黑" if self.current_language == "zh_CN" else "Dark")
        self.theme_combo.setItemText(1, "白色" if self.current_language == "zh_CN" else "White")
        self.theme_combo.setItemText(2, "灰色" if self.current_language == "zh_CN" else "Gray")
        self.title_bar.update_ui_texts(self.current_language)
        self.current_app_label.setText(
            LANGUAGES[self.current_language]["current_app"].format("无" if self.current_language == "zh_CN" else "None")
        )
        self.update_whitelist_ui_texts()
        self.update_total_time()

    def update_whitelist_ui_texts(self):
        self.whitelist_group.setTitle(LANGUAGES[self.current_language]["process_whitelist"])
        self.add_process_button.setText(LANGUAGES[self.current_language]["add_process"])
        self.select_from_tracked_button.setText(
            LANGUAGES[self.current_language].get("select_from_tracked", "选择已跟踪进程") 
            if self.current_language == "zh_CN" else "Select from Tracked"
        )
        self.remove_process_button.setText(LANGUAGES[self.current_language]["remove_selected"])

    def create_whitelist_buttons_layout(self):
        """创建白名单管理按钮布局"""
        # 创建按钮布局
        buttons_layout = QHBoxLayout()

        # 手动添加进程按钮
        self.add_process_button = QPushButton(LANGUAGES[self.current_language]["add_process"])
        self.add_process_button.clicked.connect(self.add_to_whitelist)
        buttons_layout.addWidget(self.add_process_button)
        
        # 从已跟踪进程选择按钮
        self.select_from_tracked_button = QPushButton(
            LANGUAGES[self.current_language].get("select_from_tracked", "选择已跟踪进程") 
            if self.current_language == "zh_CN" else "Select from Tracked"
        )
        self.select_from_tracked_button.clicked.connect(self.select_from_tracked_processes)
        buttons_layout.addWidget(self.select_from_tracked_button)

        # 移除选中按钮
        self.remove_process_button = QPushButton(LANGUAGES[self.current_language]["remove_selected"])
        self.remove_process_button.clicked.connect(self.remove_from_whitelist)
        buttons_layout.addWidget(self.remove_process_button)

        return buttons_layout
        
    def select_from_tracked_processes(self):
        """从已跟踪的进程列表中选择添加到白名单"""
        # 获取已跟踪的进程列表
        tracked_processes = get_tracked_processes()
        if not tracked_processes:
            QMessageBox.information(
                self, 
                LANGUAGES[self.current_language]["information"],
                LANGUAGES[self.current_language].get("no_tracked_processes", "没有已跟踪的进程。") 
                if self.current_language == "zh_CN" else "No tracked processes."
            )
            return
        
        # 创建多选对话框
        select_dialog = QDialog(self)
        select_dialog.setWindowTitle(
            LANGUAGES[self.current_language].get("select_processes", "选择进程") 
            if self.current_language == "zh_CN" else "Select Processes"
        )
        dialog_layout = QVBoxLayout()
        select_dialog.setLayout(dialog_layout)
        
        # 添加说明标签
        instruction_label = QLabel(
            LANGUAGES[self.current_language].get("select_processes_instruction", "选择要添加到白名单的进程:") 
            if self.current_language == "zh_CN" else "Select processes to add to whitelist:"
        )
        dialog_layout.addWidget(instruction_label)
        
        # 添加进程复选框
        checkboxes = []
        for process in tracked_processes:
            if process not in IGNORE_LIST:  # 只显示未在白名单中的进程
                checkbox = QCheckBox(process)
                checkboxes.append(checkbox)
                dialog_layout.addWidget(checkbox)
        
        # 添加按钮
        button_layout = QHBoxLayout()
        ok_button = QPushButton("确定" if self.current_language == "zh_CN" else "OK")
        cancel_button = QPushButton("取消" if self.current_language == "zh_CN" else "Cancel")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        dialog_layout.addLayout(button_layout)
        
        # 连接信号
        ok_button.clicked.connect(select_dialog.accept)
        cancel_button.clicked.connect(select_dialog.reject)
        
        # 显示对话框
        if select_dialog.exec_() == QDialog.Accepted:
            added_processes = []
            for checkbox in checkboxes:
                if checkbox.isChecked():
                    process_name = checkbox.text()
                    if process_name not in IGNORE_LIST:
                        self.whitelist_list.addItem(process_name)
                        IGNORE_LIST.append(process_name)
                        self.config["Process Whitelist"].append(process_name)
                        added_processes.append(process_name)
            
            if added_processes:
                save_config(self.config)
                QMessageBox.information(
                    self,
                    LANGUAGES[self.current_language]["information"],
                    (LANGUAGES[self.current_language].get("processes_added", "已添加进程: ") if self.current_language == "zh_CN" else "Added processes: ") + 
                    ", ".join(added_processes)
                )
                
    def toggle_tracking(self):
        if self.tracking:
            self.tracking_timer.stop()
            self.tracking = False
            self.toggle_tracking_button.setText(LANGUAGES[self.current_language]["start_tracking"])
        else:
            self.tracking_timer.start(1000)
            self.tracking = True
            self.toggle_tracking_button.setText(LANGUAGES[self.current_language]["stop_tracking"])
        self.update_ui_language()

    def update_current_app(self):
        """更新当前活动的应用程序信息"""
        app_name = get_active_window()
        if app_name and app_name not in IGNORE_LIST:
            self.current_app_label.setText(LANGUAGES[self.current_language]["current_app"].format(app_name))
            icon_pixmap = get_process_icon(app_name)
            self.current_icon_label.setPixmap(icon_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.current_app_label.setText(LANGUAGES[self.current_language]["current_app"].format("无" if self.current_language == "zh_CN" else "None"))
            default_pixmap = QPixmap(64, 64)
            default_pixmap.fill(Qt.gray)
            self.current_icon_label.setPixmap(default_pixmap)