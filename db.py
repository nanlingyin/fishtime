# db.py
import sqlite3
from datetime import datetime
from constants import IGNORE_LIST, APP_NAME

def init_db():
    """初始化数据库，创建表结构"""
    conn = sqlite3.connect('usage.db')
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
    conn = sqlite3.connect('usage.db')
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
    conn = sqlite3.connect('usage.db')
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

def get_application_usage_history(app_name):
    """获取特定应用的使用历史"""
    conn = sqlite3.connect('usage.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT date, SUM(duration) FROM usage
        WHERE application=?
        GROUP BY date
        ORDER BY date
    ''', (app_name,))
    data = cursor.fetchall()
    conn.close()
    return data

def clear_records():
    """清除所有使用记录"""
    conn = sqlite3.connect('usage.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM usage')
    conn.commit()
    conn.close()

def get_total_usage_time():
    """获取总的使用时间"""
    conn = sqlite3.connect('usage.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(duration) FROM usage')
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] else 0

def get_tracked_processes():
    """获取已跟踪的进程列表"""
    conn = sqlite3.connect('usage.db')
    cursor = conn.cursor()
    # 获取所有记录过的应用程序
    cursor.execute('''
        SELECT DISTINCT application FROM usage
        ORDER BY application
    ''')
    processes = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    # 过滤掉已经在忽略列表中的进程
    return [proc for proc in processes if proc and proc not in IGNORE_LIST]