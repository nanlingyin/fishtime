# process_monitor.py
import ctypes
import psutil
from ctypes import wintypes
from functools import lru_cache
import win32gui
import win32con
import win32ui
from PyQt5.QtGui import QPixmap, QIcon, QImage
from PyQt5.QtCore import Qt, QFileInfo
from PyQt5.QtWidgets import QFileIconProvider

# 使用 ctypes 获取活动窗口的窗口标题和句柄
user32 = ctypes.WinDLL('user32', use_last_error=True)

# 图标缓存
icon_cache = {}

@lru_cache(maxsize=128)
def get_process_icon(app_name):
    """
    获取进程的图标。如果无法获取，则返回默认图标。
    使用缓存减少重复获取图标的开销。
    """
    if app_name in icon_cache:
        return icon_cache[app_name]

    try:
        for proc in psutil.process_iter(['name', 'exe']):
            if proc.info['name'] == app_name:
                exe_path = proc.info['exe']
                if exe_path and os.path.exists(exe_path):
                    icon_provider = QFileIconProvider()
                    qt_icon = icon_provider.icon(QFileInfo(exe_path))
                    pixmap = qt_icon.pixmap(64, 64)
                    icon_cache[app_name] = pixmap
                    return pixmap
    except Exception as e:
        print(f"获取 {app_name} 图标时出错: {e}")

    # 返回默认图标
    default_icon = QPixmap(64, 64)
    default_icon.fill(Qt.gray)
    icon_cache[app_name] = default_icon
    return default_icon

def hicon_to_qpixmap(hicon):
    """
    将 HICON 转换为 QPixmap
    """
    # 获取 icon info
    info = win32gui.GetIconInfo(hicon)
    bmp = info[2]
    width = win32gui.GetSystemMetrics(win32con.SM_CXICON)
    height = win32gui.GetSystemMetrics(win32con.SM_CYICON)

    # Create a device context
    hdc = win32gui.CreateCompatibleDC(0)
    hbmp = win32ui.CreateBitmap()
    hbmp.CreateCompatibleBitmap(win32ui.CreateDCFromHandle(hdc), width, height)
    hdc_obj = win32ui.CreateDCFromHandle(hdc)
    hdc_obj.SelectObject(hbmp)
    win32gui.DrawIconEx(hdc, 0, 0, hicon, width, height, 0, None, win32con.DI_NORMAL)

    # Get bitmap bits
    bmp_info = hbmp.GetInfo()
    bmp_str = hbmp.GetBitmapBits(True)

    # Create QImage from bitmap bits
    image = QImage(bmp_str, bmp_info['bmWidth'], bmp_info['bmHeight'], QImage.Format_ARGB32)
    pixmap = QPixmap.fromImage(image)

    # Clean up
    win32gui.DeleteObject(bmp)
    win32gui.DeleteObject(info[1])  # hbmColor
    win32gui.DeleteObject(info[0])  # hbmMask
    win32gui.DeleteDC(hdc)
    hdc_obj.DeleteDC()

    return pixmap

def get_active_window():
    """
    获取当前活动窗口的进程名称
    """
    hwnd = user32.GetForegroundWindow()
    length = user32.GetWindowTextLengthW(hwnd)
    buffer = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(hwnd, buffer, length + 1)
    window_title = buffer.value
    if window_title:
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        try:
            process = psutil.Process(pid.value)
            return process.name()
        except Exception:
            return None
    else:
        return None

# Win32 API 结构体定义
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ('biSize', wintypes.DWORD),
        ('biWidth', wintypes.LONG),
        ('biHeight', wintypes.LONG),
        ('biPlanes', wintypes.WORD),
        ('biBitCount', wintypes.WORD),
        ('biCompression', wintypes.DWORD),
        ('biSizeImage', wintypes.DWORD),
        ('biXPelsPerMeter', wintypes.LONG),
        ('biYPelsPerMeter', wintypes.LONG),
        ('biClrUsed', wintypes.DWORD),
        ('biClrImportant', wintypes.DWORD),
    ]

class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ('bmiHeader', BITMAPINFOHEADER),
        ('bmiColors', wintypes.DWORD * 3),
    ]

# 导入os模块
import os