import sys


def pytest_configure(config):
    sys._called_from_test = True
