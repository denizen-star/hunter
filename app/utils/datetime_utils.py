"""Date and time utility functions"""
from datetime import datetime
import pytz


def get_est_now() -> datetime:
    """Get current datetime in EST timezone"""
    est = pytz.timezone('America/Toronto')
    return datetime.now(est)


def format_datetime_for_filename(dt: datetime = None) -> str:
    """Format datetime for use in filenames: YYYYMMDDHHMMSS"""
    if dt is None:
        dt = get_est_now()
    return dt.strftime("%Y%m%d%H%M%S")


def format_for_display(dt: datetime) -> str:
    """Format datetime for display: Oct 13, 2025 2:30 PM"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    return dt.strftime("%b %d, %Y %I:%M %p")


def parse_datetime(dt_str: str) -> datetime:
    """Parse ISO format datetime string"""
    return datetime.fromisoformat(dt_str)

