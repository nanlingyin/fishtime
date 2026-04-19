import sys

if sys.platform == "win32":
    from .monitor_win import (
        get_active_window,
        get_process_icon,
        send_notification,
    )
elif sys.platform == "darwin":
    from .monitor_mac import (
        get_active_window,
        get_process_icon,
        send_notification,
    )
else:
    from .monitor_stub import (
        get_active_window,
        get_process_icon,
        send_notification,
    )

__all__ = ["send_notification", "get_process_icon", "get_active_window"]
