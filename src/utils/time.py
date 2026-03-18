from datetime import datetime


def get_current_date():
    """
    Returns the current date in YYYY-MM-DD format
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_date_window(start_date=None, end_date=None):
    """
    Returns start and end dates for analysis window.
    If dates not provided, defaults to last 30 days up to current date.

    Args:
        start_date (str, optional): Start date in YYYY-MM-DD format
        end_date (str, optional): End date in YYYY-MM-DD format

    Returns:
        tuple: (start_date, end_date) strings in YYYY-MM-DD format
    """
    today = datetime.now()

    if end_date is None:
        end_date = today.strftime("%Y-%m-%d")

    if start_date is None:
        from datetime import timedelta

        start = today - timedelta(days=7)
        start_date = start.strftime("%Y-%m-%d")

    return start_date, end_date
