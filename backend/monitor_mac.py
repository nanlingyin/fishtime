"""macOS platform implementation: active window tracking, app icons, and notifications."""

import base64
import re
import subprocess
from functools import lru_cache

try:
    from AppKit import NSWorkspace, NSBitmapImageRep, NSBitmapImageFileTypePNG
    HAS_APPKIT = True
except ImportError:
    HAS_APPKIT = False

icon_cache = {}


def send_notification(title, message):
    try:
        # Escape double quotes to avoid breaking the AppleScript string
        safe_title = title.replace('"', '\\"')
        safe_msg = message.replace('"', '\\"')
        script = f'display notification "{safe_msg}" with title "{safe_title}"'
        subprocess.run(["osascript", "-e", script], check=False, timeout=5)
    except Exception as e:
        print(f"Notification failed: {e}")


def _nsimage_to_base64(image):
    try:
        image.setSize_((64, 64))
        tiff_data = image.TIFFRepresentation()
        bitmap = NSBitmapImageRep.imageRepWithData_(tiff_data)
        if bitmap is None:
            return None
        png_data = bitmap.representationUsingType_properties_(
            NSBitmapImageFileTypePNG, None
        )
        if png_data is None:
            return None
        return base64.b64encode(bytes(png_data)).decode("utf-8")
    except Exception as e:
        print(f"Error converting NSImage to base64: {e}")
        return None


@lru_cache(maxsize=128)
def get_process_icon(app_name):
    if app_name in icon_cache:
        return icon_cache[app_name]

    if not HAS_APPKIT:
        return None

    try:
        workspace = NSWorkspace.sharedWorkspace()
        for app in workspace.runningApplications():
            if app.localizedName() == app_name:
                bundle_url = app.bundleURL()
                if bundle_url:
                    path = bundle_url.path()
                    icon = workspace.iconForFile_(path)
                    if icon:
                        b64 = _nsimage_to_base64(icon)
                        if b64:
                            icon_cache[app_name] = b64
                            return b64
    except Exception as e:
        print(f"Error getting icon for {app_name}: {e}")

    return None


def get_active_window():
    # lsappinfo directly queries launchservicesd — always fresh, no permissions needed,
    # and works correctly from background threads (unlike NSWorkspace which may cache
    # stale state when there's no Cocoa NSRunLoop on the calling thread).
    try:
        front = subprocess.run(
            ["lsappinfo", "front"],
            capture_output=True, text=True, timeout=2,
        )
        front_id = front.stdout.strip()
        if front_id:
            info = subprocess.run(
                ["lsappinfo", "info", "-only", "name", front_id],
                capture_output=True, text=True, timeout=2,
            )
            # Output format: "Name" = "Google Chrome"\n
            match = re.search(r'"(?:LSDisplay)?Name"\s*=\s*"([^"]+)"', info.stdout)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"lsappinfo error: {e}")

    # Fallback: AppKit (may be stale in background threads, but better than nothing)
    if HAS_APPKIT:
        try:
            workspace = NSWorkspace.sharedWorkspace()
            app = workspace.frontmostApplication()
            if app:
                name = app.localizedName()
                if name:
                    return name
        except Exception as e:
            print(f"AppKit error getting active window: {e}")

    return None
