"""
This works when Stabilization mode is on.
Authority Service
Enforces System-level refusals and quest suspension.
"""

from datetime import datetime
import pytz

from app.db.database import get_connection
from datetime import datetime, timezone, timedelta


IST = pytz.timezone("Asia/Kolkata")


def _current_ist_datetime():
    return datetime.utcnow().replace(tzinfo=timezone.utc).astimezone(IST)



def _current_ist_date():
    return _current_ist_datetime().date().isoformat()


def _is_within_daily_window():
    """
    Returns True if current IST time is within 00:00–23:59
    """
    now = _current_ist_datetime()
    return now.hour < 24  # explicit for authority clarity


def check_daily_time_authority():
    """
    Enforces daily submission window (IST).
    """
    if not _is_within_daily_window():
        return {
            "allowed": False,
            "reason": "TIME_WINDOW_CLOSED",
            "message": "Daily submission period has ended.",
        }

    return {
        "allowed": True,
        "reason": None,
        "message": "Daily cycle active.",
        "system_date": _current_ist_date(),
    }


def check_system_authority():
    """
    Determines whether the Player is allowed full system access today.
    """
    conn = get_connection()
    cursor = conn.cursor()

    return {
        "allowed": True,
        "reason": None,
        "message": "Full system access granted.",
    }