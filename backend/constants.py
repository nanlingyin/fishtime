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
]

APP_NAME = "FishTime"
