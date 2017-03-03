from datetime import datetime as dt
from datetime import timedelta as td

import logging

from tabulate import tabulate


logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
