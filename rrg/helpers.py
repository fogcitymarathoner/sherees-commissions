
from datetime import datetime as dt


class MissingEnvVar(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def date_to_datetime(date):
    return dt(year=date.year, month=date.month, day=date.day)