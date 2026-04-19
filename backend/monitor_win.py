import ctypes
import psutil
from ctypes import wintypes
from functools import lru_cache
import win32gui
import win32con
import win32ui
import win32api
from PIL import Image
import io
import base64
import os
from win10toast import ToastNotifier

toaster = ToastNotifier()

def send_notification(title, message):
    try:
        toaster.show_toast(title, message, duration=5, threaded=True)
    except Exception as e:
        print(f"Notification failed: {e}")

user32 = ctypes.WinDLL('user32', use_last_error=True)

# Icon cache
icon_cache = {}
# Name cache
name_cache = {}

def hicon_to_base64(hicon):
    """
    Convert HICON to base64 PNG string using Pillow
    """
    try:
        # Get icon info
        info = win32gui.GetIconInfo(hicon)
        if not info:
            return None
            
        width = win32gui.GetSystemMetrics(win32con.SM_CXICON)
        height = win32gui.GetSystemMetrics(win32con.SM_CYICON)

        # Create a device context
        hdc = win32gui.CreateCompatibleDC(0)
        hbmp = win32ui.CreateBitmap()
        hbmp.CreateCompatibleBitmap(win32ui.CreateDCFromHandle(hdc), width, height)
        hdc_obj = win32ui.CreateDCFromHandle(hdc)
        hdc_obj.SelectObject(hbmp)
        
        # Draw the icon
        win32gui.DrawIconEx(hdc, 0, 0, hicon, width, height, 0, None, win32con.DI_NORMAL)

        # Get bitmap bits
        bmp_info = hbmp.GetInfo()
        bmp_str = hbmp.GetBitmapBits(True)

        # Create PIL Image from bitmap bits
        # Windows bitmaps are usually BGRA
        image = Image.frombuffer(
            'RGBA', 
            (bmp_info['bmWidth'], bmp_info['bmHeight']), 
            bmp_str, 'raw', 'BGRA', 0, 1
        )

        # Save to BytesIO
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Clean up
        if info[4]: win32gui.DeleteObject(info[4])
        if info[3]: win32gui.DeleteObject(info[3])
        
        win32gui.DeleteDC(hdc)
        hdc_obj.DeleteDC()
        
        return img_str
    except Exception as e:
        print(f"Error converting icon: {e}")
        return None

@lru_cache(maxsize=128)
def get_process_icon(app_name):
    if app_name in icon_cache:
        return icon_cache[app_name]

    try:
        for proc in psutil.process_iter(['name', 'exe']):
            # We might need to match against friendly name or exe name
            # But here app_name is what we stored in DB.
            # If we store friendly name, we might not find the process by name easily.
            # But let's assume we can find it.
            if proc.info['name'] == app_name:
                exe_path = proc.info['exe']
                if exe_path and os.path.exists(exe_path):
                    try:
                        large, small = win32gui.ExtractIconEx(exe_path, 0)
                        if large:
                            hicon = large[0]
                            b64 = hicon_to_base64(hicon)
                            win32gui.DestroyIcon(hicon)
                            if b64:
                                icon_cache[app_name] = b64
                                return b64
                    except Exception:
                        pass
    except Exception as e:
        print(f"Error getting icon for {app_name}: {e}")

    return None

def get_file_description(path):
    """
    Get the FileDescription from the executable version info.
    """
    try:
        # Get language and codepage
        info = win32api.GetFileVersionInfo(path, '\\')
        lang, codepage = win32api.GetFileVersionInfo(path, '\\VarFileInfo\\Translation')[0]
        
        # Construct the query string
        # lang and codepage are integers, need to format as hex string
        str_info = u'\\StringFileInfo\\%04X%04X\\FileDescription' % (lang, codepage)
        
        description = win32api.GetFileVersionInfo(path, str_info)
        return description
    except Exception:
        return None

def get_friendly_name(exe_path, exe_name):
    """
    Get friendly name from cache or file description
    """
    if exe_name in name_cache:
        return name_cache[exe_name]
        
    if not exe_path or not os.path.exists(exe_path):
        return exe_name
        
    description = get_file_description(exe_path)
    if description:
        name_cache[exe_name] = description
        return description
    
    name_cache[exe_name] = exe_name
    return exe_name

def get_active_window():
    """
    Get current active window process name (friendly name if possible)
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
            exe_name = process.name()
            exe_path = None
            try:
                exe_path = process.exe()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass
                
            friendly_name = get_friendly_name(exe_path, exe_name)
            
            # Filter out common system/background processes that might grab focus momentarily
            # or just clean up names
            if friendly_name:
                # If it looks like a file path or exe, try to clean it
                if friendly_name.lower().endswith('.exe'):
                    friendly_name = friendly_name[:-4]
                    # Capitalize first letter if it was all lowercase
                    if friendly_name.islower():
                        friendly_name = friendly_name.title()
            
            return friendly_name
        except Exception:
            return None
    else:
        return None
