# ui/report.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
import db
from constants import LANGUAGES, IGNORE_LIST
from utils import export_to_xlsx, export_to_csv, export_to_pdf
from process_monitor import get_process_icon

def generate_report(language):
    """
    生成并显示表格报告，支持导出为不同格式
    """
    data = db.get_daily_usage_data()
    if not data:
        QMessageBox.information(None, LANGUAGES[language]["information"], LANGUAGES[language]["no_usage"])
        return

    # 创建表格对话框
    table_dialog = QDialog()
    table_dialog.setWindowTitle(LANGUAGES[language]["report"])
    table_dialog.setGeometry(200, 200, 900, 600)
    layout = QVBoxLayout()
    table_dialog.setLayout(layout)

    table = QTableWidget()
    table.setRowCount(len(data))
    table.setColumnCount(5)  # 应用名称，使用时长（秒），使用时长（分钟），使用时长（小时），图标
    table.setHorizontalHeaderLabels([
        LANGUAGES[language]["application"],
        LANGUAGES[language]["duration_seconds"],
        LANGUAGES[language]["duration_minutes"],
        LANGUAGES[language]["duration_hours"],
        "图标" if language == "zh_CN" else "Icon"
    ])
    table.setIconSize(QSize(64, 64))  # 设置图标尺寸
    table.setSelectionBehavior(QTableWidget.SelectRows)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    max_duration = max([duration for _, duration in data]) if data else 1

    for row, (app, duration) in enumerate(data):
        if app and app not in IGNORE_LIST:
            # 应用名称
            app_item = QTableWidgetItem(app)
            table.setItem(row, 0, app_item)

            # 使用时长（秒）
            table.setItem(row, 1, QTableWidgetItem(str(duration)))

            # 使用时长（分钟）
            minutes = duration / 60
            table.setItem(row, 2, QTableWidgetItem(f"{minutes:.2f}"))

            # 使用时长（小时）
            hours = duration / 3600
            table.setItem(row, 3, QTableWidgetItem(f"{hours:.2f}"))

            # 获取并设置应用图标
            icon_pixmap = get_process_icon(app)
            icon_label = QLabel()
            icon_label.setPixmap(icon_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            icon_label.setAlignment(Qt.AlignCenter)
            table.setCellWidget(row, 4, icon_label)

            # 设置单元格背景颜色根据使用时长
            intensity = min(int((duration / max_duration) * 255), 255)
            color = QColor(intensity, 255 - intensity, 55)  # 从红到绿
            for col in range(4):
                table.item(row, col).setBackground(color)

    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)
    table.verticalHeader().setDefaultSectionSize(70)
    layout.addWidget(table)

    # 导出按钮布局
    export_layout = QHBoxLayout()
    export_layout.addStretch()

    # 导出为 XLSX
    export_xlsx_button = QPushButton("导出为 XLSX" if language == "zh_CN" else "Export as XLSX")
    export_xlsx_button.setFixedHeight(50)
    export_xlsx_button.setStyleSheet("""
        QPushButton {
            background-color: #5A67D8;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 18px;
            font-family: "Microsoft YaHei";
        }
        QPushButton:hover {
            background-color: #434190;
        }
    """)
    export_xlsx_button.clicked.connect(lambda: export_to_xlsx(data, language))
    export_layout.addWidget(export_xlsx_button)

    # 导出为 CSV
    export_csv_button = QPushButton(LANGUAGES[language]["export_csv"])
    export_csv_button.setFixedHeight(50)
    export_csv_button.setStyleSheet("""
        QPushButton {
            background-color: #38A169;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 18px;
            font-family: "Microsoft YaHei";
        }
        QPushButton:hover {
            background-color: #2F855A;
        }
    """)
    export_csv_button.clicked.connect(lambda: export_to_csv(data, language))
    export_layout.addWidget(export_csv_button)

    # 导出为 PDF
    export_pdf_button = QPushButton(LANGUAGES[language].get("export_pdf", "Export as PDF"))
    export_pdf_button.setFixedHeight(50)
    export_pdf_button.setStyleSheet("""
        QPushButton {
            background-color: #DD6B20;
            color: white;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 18px;
            font-family: "Microsoft YaHei";
        }
        QPushButton:hover {
            background-color: #C05621;
        }
    """)
    export_pdf_button.clicked.connect(lambda: export_to_pdf(data, language))
    export_layout.addWidget(export_pdf_button)

    layout.addLayout(export_layout)

    table_dialog.exec_()

def show_chart(app_name, language):
    """
    显示特定应用的使用时间历史图表
    """
    data = db.get_application_usage_history(app_name)
    
    if not data:
        QMessageBox.information(None, LANGUAGES[language]["information"], LANGUAGES[language]["no_usage"])
        return

    dates = [row[0] for row in data]
    durations = [row[1] for row in data]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(dates, durations, marker='o', linestyle='-')
    ax.set_title(f"{app_name} 使用时长" if language == "zh_CN" else f"Usage Duration of {app_name}")
    ax.set_xlabel("日期" if language == "zh_CN" else "Date")
    ax.set_ylabel("秒数" if language == "zh_CN" else "Seconds")
    plt.xticks(rotation=45)
    plt.tight_layout()

    chart_dialog = QDialog()
    chart_dialog.setWindowTitle(f"{app_name} {LANGUAGES[language]['report']}")
    chart_dialog.setGeometry(250, 250, 800, 600)
    layout = QVBoxLayout()
    chart_dialog.setLayout(layout)

    canvas = FigureCanvas(fig)
    layout.addWidget(canvas)

    chart_dialog.exec_()