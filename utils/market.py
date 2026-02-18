from datetime import date

def is_market_holiday(d: date) -> bool:
    """
    Check if the date is a known global market holiday.
    Forex market is closed on:
    - New Year's Day (Jan 1)
    - Christmas (Dec 25)
    """
    if d.month == 1 and d.day == 1:
        return True
    if d.month == 12 and d.day == 25:
        return True
    return False
