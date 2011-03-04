import datetime

def last_day_of_month(year, month):
    """
    Return a date object representing the last day of the specified month
    """
    # This is annoyingly hard: Figure out the number of days in the current month.
    # Suggenstions for improvements are welcome!
    # We begin by constructing a day object representing the first day in the specified month.
    tmp = datetime.date(year, month, 1)
    # Move forwards 31 days to an an arbitrary day in the next month
    tmp = tmp + datetime.timedelta(31)
    # Move tmp to be the first in the next month
    tmp = datetime.date(tmp.year,tmp.month,1)
    # Then move it backwards one more day to the last of the current month
    return tmp - datetime.timedelta(1)

def first_day_of_week(year, week):
    """
    Return a date object representing the first day of the specified week
    """
    start = datetime.date(year, 1, 7)
    nyear, nweek, nweekday = start.isocalendar()
    assert nyear == year
    return start + datetime.timedelta(7 * (week - nweek) - (nweekday - 1))

def last_day_of_week(year, week):
    """
    Return a date object representing the last day of the specified week
    """
    return first_day_of_week(year, week) + datetime.timedelta(6)
