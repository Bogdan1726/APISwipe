from datetime import datetime, timedelta
import calendar


def get_range_month(date_start=None):
    """
    Returns the month ahead of the current date
    """
    date = datetime.now()
    if date_start:
        date = date_start
    days_in_month = calendar.monthrange(date.year, date.month)[1]
    date += timedelta(days=days_in_month)
    return date
