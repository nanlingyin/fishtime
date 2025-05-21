# app.py
"""
摸鱼时间追踪器 - 记录应用使用时间并可视化
"""
import sys
import os

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from db import init_db
from config import load_config, save_config

def main():
    """主函数，程序入口"""
    try:
        import psutil
        import openpyxl
        from fpdf import FPDF
        import win32gui
        import win32con
        import win32ui
    except ImportError:
        print("缺少必要的依赖项，请运行以下命令安装：")
        print("pip install psutil PyQt5 matplotlib openpyxl fpdf pywin32")
        sys.exit(1)

    # 环境变量设置（如有必要）
    if 'QT_QPA_PLATFORM_PLUGIN_PATH' not in os.environ:
        try:
            import site
            site_packages = site.getsitepackages()[0]
            qt_plugin_path = os.path.join(site_packages, r"PyQt5\Qt5\plugins\platforms")
            if os.path.exists(qt_plugin_path):
                os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = qt_plugin_path
        except Exception as e:
            print(f"设置 Qt 插件路径时出错: {e}")

    # 初始化数据库
    init_db()
    
    # 加载配置
    config = load_config()
    save_config(config)
    
    # 启动应用
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()