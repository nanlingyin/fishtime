# constants.py
import os

# 配置文件路径
CONFIG_FILE = 'config.json'

# 默认配置
DEFAULT_CONFIG = {
    "font_family": "Microsoft YaHei",
    "font_color": "#2E3440",
    "language": "zh_CN",
    "theme": "灰色",
    "Process Whitelist": []
}

# 忽略列表，添加不需要监控的进程名称
IGNORE_LIST = [
    "Idle", "System", "Registry", "Memory Compression",
    "摸鱼时间记录.exe", "python.exe",
    "选择背景图片", "选择字体颜色", "选择字体", "编辑背景图片",
    "确认清除", "完成", "字体设置", "Figure"
]

APP_NAME = "摸鱼时间记录.exe"  # 确保这是应用的实际进程名称

# 语言定义
LANGUAGES = {
    "zh_CN": {
        "fish": "总摸鱼时长: ",
        "current_app": "当前应用: {}",
        "no_usage": "今日无使用记录。",
        "export_success": "报告已保存至 {}",
        "export_error": "保存文件时出错: {}",
        "clear_confirm_title": "确认清除",
        "clear_confirm_text": "确定要清除所有记录吗？",
        "clear_success": "记录已清除。",
        "font_settings": "字体设置",
        "report": "生成报告",
        "clear": "清除记录",
        "font_setting_button": "字体设置",
        "tray_show": "显示",
        "tray_exit": "退出",
        "tray_minimized": "应用已最小化到系统托盘。",
        "information": "信息",
        "error": "错误",
        "application": "应用/进程",
        "duration_seconds": "使用时长（秒）",
        "duration_minutes": "使用时长（分钟）",
        "duration_hours": "使用时长（小时）",
        "start_tracking": "开始跟踪",
        "stop_tracking": "停止跟踪",
        "export_csv": "导出为 CSV",
        "export_pdf": "导出为 PDF",
        "dark_mode": "暗黑模式",
        "chart": "图表",
        "none": "无",
        "process_whitelist": "进程白名单",
        "add_process": "添加进程",
        "remove_selected": "移除选中",
        # 关闭对话框相关字符串
        "close_dialog_title": "关闭确认",
        "close_dialog_text": "您想要将应用最小化到托盘吗？",
        "close_dialog_yes": "最小化到托盘",
        "close_dialog_no": "退出应用",
        "close_dialog_cancel": "取消",
    },
    "en_US": {
        "fish": "Slackoff Time：",
        "current_app": "Current Application: {}",
        "no_usage": "No usage records today.",
        "export_success": "Report saved to {}",
        "export_error": "Error saving file: {}",
        "clear_confirm_title": "Confirm Clear",
        "clear_confirm_text": "Are you sure you want to clear all records?",
        "clear_success": "Records cleared.",
        "font_settings": "Font Settings",
        "report": "Generate Report",
        "clear": "Clear Records",
        "font_setting_button": "Font Settings",
        "tray_show": "Show",
        "tray_exit": "Exit",
        "tray_minimized": "Application minimized to system tray.",
        "information": "Information",
        "error": "Error",
        "application": "Application/Process",
        "duration_seconds": "Usage Duration (seconds)",
        "duration_minutes": "Usage Duration (minutes)",
        "duration_hours": "Usage Duration (hours)",
        "start_tracking": "Start Tracking",
        "stop_tracking": "Stop Tracking",
        "export_csv": "Export as CSV",
        "export_pdf": "Export as PDF",
        "dark_mode": "Dark Mode",
        "chart": "Chart",
        "none": "none",
        "process_whitelist": "Process Whitelist",
        "add_process": "Add Process",
        "remove_selected": "Remove Selected",
        # 关闭对话框相关字符串
        "close_dialog_title": "Close Confirmation",
        "close_dialog_text": "Do you want to minimize the application to the system tray?",
        "close_dialog_yes": "Minimize to Tray",
        "close_dialog_no": "Exit Application",
        "close_dialog_cancel": "Cancel",
    }
}

# 主题定义
THEMES = {
    "灰色": """
        QMainWindow {{
            background-color: #A0AEC0;
            font-family: "{font_family}";
            color: {font_color};
        }}
        QPushButton {{
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            background-color: #5A67D8;
            color: white;
            font-size: 16px;
            font-family: "{font_family}";
        }}
        QPushButton:hover {{
            background-color: #434190;
        }}
        QPushButton:pressed {{
            background-color: #2B6CB0;
        }}
        QDialog {{
            background-color: #FFFFFF;
            font-family: "{font_family}";
        }}
        QLabel {{
            font-size: 18px;
            font-family: "{font_family}";
        }}
        QTableWidget {{
            font-family: "{font_family}";
            font-size: 14px;
            alternatingRowColors: true;
            background-color: #FFFFFF;
            gridline-color: #CBD5E0;
        }}
        QTableWidget::item:selected {{
            background-color: #A0AEC0;
            color: white;
        }}
    """,
    "白色": """
        QMainWindow {{
            background-color: #FFFFFF;
            font-family: "{font_family}";
            color: {font_color};
        }}
        QPushButton {{
            border: 1px solid #CCCCCC;
            border-radius: 8px;
            padding: 12px 24px;
            background-color: #F0F0F0;
            color: black;
            font-size: 16px;
            font-family: "{font_family}";
        }}
        QPushButton:hover {{
            background-color: #E0E0E0;
        }}
        QPushButton:pressed {{
            background-color: #D0D0D0;
        }}
        QDialog {{
            background-color: #FFFFFF;
            font-family: "{font_family}";
        }}
        QLabel {{
            font-size: 18px;
            font-family: "{font_family}";
        }}
        QTableWidget {{
            font-family: "{font_family}";
            font-size: 14px;
            alternatingRowColors: true;
            background-color: #FFFFFF;
            gridline-color: #CCCCCC;
        }}
        QTableWidget::item:selected {{
            background-color: #D0D0D0;
            color: black;
        }}
    """,
    "暗黑": """
        QMainWindow {{
            background-color: #2D3748;
            font-family: "{font_family}";
            color: {font_color};
        }}
        QPushButton {{
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            background-color: #4A5568;
            color: white;
            font-size: 16px;
            font-family: "{font_family}";
            font-weight: bold;
        }}
        QPushButton:hover {{
            background-color: #2D3748;
        }}
        QPushButton:pressed {{
            background-color: #1A202C;
        }}
        QDialog {{
            background-color: #1A202C;
            font-family: "{font_family}";
        }}
        QLabel {{
            font-size: 18px;
            font-family: "{font_family}";
            color: {font_color};
        }}
        QTableWidget {{
            font-family: "{font_family}";
            font-size: 14px;
            alternatingRowColors: true;
            background-color: #2D3748;
            gridline-color: #4A5568;
        }}
        QTableWidget::item:selected {{
            background-color: #4A5568;
            color: white;
        }}
    """
}

# 创建确保UI目录存在
def ensure_ui_dir_exists():
    if not os.path.exists('ui'):
        os.makedirs('ui')

# 创建UI目录
ensure_ui_dir_exists()