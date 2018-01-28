import calendar
from datetime import datetime as dt
from datetime import timedelta as td

"""
Python utility library for payroll calendars - weekly, biweekly, semimonthly
and monthly

https://payroll.unca.edu/sites/default/files/2016%20Payroll%20Calendar.pdf`
"""


def add_one_month(t):
    """Return a `datetime.date` or `datetime.datetime` (as given) that is
    one month earlier.
    
    Note that the resultant day of the month might change if the following
    month has fewer days:
    
        >>> add_one_month(datetime.date(2010, 1, 31))
        datetime.date(2010, 2, 28)
    """
    one_day = td(days=1)
    one_month_later = t + one_day
    while one_month_later.month == t.month:  # advance to start of next month
        one_month_later += one_day
    target_month = one_month_later.month
    while one_month_later.day < t.day:  # advance to appropriate day
        one_month_later += one_day
        if one_month_later.month != target_month:  # gone too far
            one_month_later -= one_day
            break
    return one_month_later


def next_sunday(date):
    if date.weekday() == 6:
        next_sunday = date
    else:
        day = date
        while day < date + td(days=7):
            day = day + td(days=1)
        
            if day.weekday()== 6:
                break
        next_sunday = day
    return next_sunday


def previous_monday(date):
    if date.weekday() == 0:
        return date
    else:
        day = date
        while day > date - td(days=7):
            day = day - td(days=1)
        
            if day.weekday()== 0:
                break
        previous_monday = day
    return previous_monday


def current_week(date):
    period_start = previous_monday(date)
    period_end = next_sunday(date)
    return period_start, period_end


def current_month(date):
    period_start = dt(year=date.year,
                      month=date.month,
                      day=1)

    period_end = add_one_month(dt(year=date.year, month=date.month, day=1)) - td(days=1)
    return period_start, period_end


def last_monday_previous_year(date):
    jan1 = dt(year=date.year, month=1, day=1)
    mon = jan1
    while mon.weekday() != 0:
        
        mon = mon - td(days=1)
    return mon


def first_biweek_of_year(date):
    return last_monday_previous_year(dt.now()), \
        last_monday_previous_year(dt.now()) + td(days=13)


def next_biweek(start, end):
    return start + td(14), end + td(14)


def next_week(start, end):
    return start + td(7), end + td(7)


def next_month(start, end):
    if start.month != end.month:
        print('start and end month are different')
    if start.month < 12:
        return (dt(year=start.year, month=start.month + 1, day=start.day),
                dt(year=end.year, month=end.month + 1, day=calendar.monthrange(end.year, end.month + 1)[1]))
    else:
        return (dt(year=start.year + 1, month=1, day=start.day),
                dt(year=end.year + 1, month=1, day=calendar.monthrange(end.year, 1)[1]))


def next_semimonth(start, end):
    if end.day == 15:

        if end.month < 12:
            return (dt(year=start.year, month=start.month, day=16),
                    dt(year=end.year, month=end.month + 1 if end.month < 12 else 1, day=1) -
                    td(days=1))
        else:
            if end.day < 16:
                return (dt(year=end.year, month=end.month, day=16),
                        dt(year=end.year, month=end.month, day=calendar.monthrange(end.year, end.month)[1]))
    else:
        if end.month < 12:
            return (dt(year=start.year, month=start.month + 1, day=1),
                    dt(year=end.year, month=end.month + 1, day=15))
        else:
            return (dt(year=start.year + 1, month=1, day=1),
                    dt(year=start.year + 1, month=1, day=15))


def current_semimonth(date):
    if date.day < 16:
        return (dt(year=date.year, month=date.month, day=1),
                dt(year=date.year, month=date.month, day=15))
    else:
        return (dt(year=date.year, month=date.month, day=16),
                dt(year=date.year, month=date.month, day=calendar.monthrange(date.year, date.month)[1]))


def current_biweek(date):
    start, end = first_biweek_of_year(date)
    if date >= start and date <= end + td(days=1):
        return start, end

    else:
        while date >= start and date >= end + td(days=1):
            start, end = next_biweek(start, end)
            
    return start, end

# todo: write unittest for weeks_between_dates
