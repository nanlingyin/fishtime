# db.py
import sqlite3
from datetime import datetime
from .constants import IGNORE_LIST, APP_NAME

DB_FILE = 'usage.db'

def init_db():
    """初始化数据库，创建表结构"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY,
            application TEXT,
            duration INTEGER,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_usage(app_name, duration):
    """记录应用使用时间"""
    # 如果应用在忽略列表中，不记录
    if app_name in IGNORE_LIST or app_name == APP_NAME:
        return
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    date_str = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
        INSERT INTO usage (application, duration, date)
        VALUES (?, ?, ?)
    ''', (app_name, duration, date_str))
    conn.commit()
    conn.close()

def get_daily_usage_data():
    """获取当天的使用数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT application, SUM(duration) FROM usage
        WHERE date=?
        GROUP BY application
        ORDER BY SUM(duration) DESC
    ''', (datetime.now().strftime("%Y-%m-%d"),))
    data = cursor.fetchall()
    conn.close()
    return data

def get_all_usage_data():
    """获取所有历史数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT application, SUM(duration) FROM usage
        GROUP BY application
        ORDER BY SUM(duration) DESC
    ''')
    data = cursor.fetchall()
    conn.close()
    return data

def get_weekly_usage_data():
    """获取过去7天的使用数据"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # SQLite 'date' modifier usage for last 7 days
    cursor.execute('''
        SELECT application, SUM(duration) FROM usage
        WHERE date >= date('now', '-6 days')
        GROUP BY application
        ORDER BY SUM(duration) DESC
    ''')
    data = cursor.fetchall()
    conn.close()
    return data
