import sys
import pytest

def pytest_configure(config):
    sys._called_from_test = True
