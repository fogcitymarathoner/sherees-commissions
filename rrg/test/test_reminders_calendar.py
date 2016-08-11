import sys
from datetime import datetime as dt

import logging
from rrg.reminders import current_week
from rrg.reminders import current_semiweek
from rrg.reminders import current_month
from rrg.reminders import first_biweek_of_year
from rrg.reminders import next_biweek
from rrg.reminders import current_biweek
from rrg.reminders import biweeks_between_dates
from rrg.reminders import weeks_between_dates

from rrg.reminders import previous_monday
from rrg.reminders import next_sunday

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')


class Test:

    def setup_class(self):

        self.payroll_run_date = dt(year=2016, month=8, day=8)

    def test_in_test(self):
        """
        test _called_from_test
        :return:
        """
        assert sys._called_from_test

    def test_previous_monday(self, capsys):
        """
        test previous_monday():
        """
        logger.debug('day of week')
        logger.debug(self.payroll_run_date.weekday())
        out, err = capsys.readouterr()
        print(out, err)
        monday = previous_monday(self.payroll_run_date)

        logger.debug('monday')
        logger.debug(monday)
        assert dt(year=2016, month=8, day=8) == monday

    def test_next_sunday(self):
        """
        test next_sunday
        """

        sunday = next_sunday(self.payroll_run_date)
        assert dt(year=2016, month=8, day=14) == sunday

    def test_reminders(self):
        """


        """
        # current week 8/8/2015 - 8/14/2015
        period_start, period_end = current_week(self.payroll_run_date)
        assert dt(year=2016, month=8, day=8) == period_start
        assert dt(year=2016, month=8, day=14) == period_end

        # current semiweek
        period_start, period_end = current_semiweek(self.payroll_run_date)
        assert dt(year=2016, month=8, day=1) == period_start
        assert dt(year=2016, month=8, day=15) == period_end

        # current month
        period_start, period_end = current_month(self.payroll_run_date)
        assert dt(year=2016, month=8, day=1) == period_start
        assert dt(year=2016, month=8, day=31) == period_end

        # first biweek
        period_start, period_end = first_biweek_of_year(self.payroll_run_date)
        assert dt(year=2015, month=12, day=28) == period_start
        assert dt(year=2016, month=1, day=10) == period_end

        period_start, period_end = next_biweek(*first_biweek_of_year(self.payroll_run_date))
        assert dt(year=2016, month=1, day=11) == period_start
        assert dt(year=2016, month=1, day=24) == period_end
        # current_biweek
        period_start, period_end = current_biweek(self.payroll_run_date)
        assert dt(year=2016, month=8, day=8) == period_start
        assert dt(year=2016, month=8, day=21) == period_end
    
        biweeks = biweeks_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)
        assert len(biweeks) == 4
        assert biweeks[0] == (dt(year=2016, month=6, day=27), dt(year=2016, month=7, day=10))
        assert biweeks[1] == (dt(year=2016, month=7, day=11), dt(year=2016, month=7, day=24))
        assert biweeks[2] == (dt(year=2016, month=7, day=25), dt(year=2016, month=8, day=7)) 
        assert biweeks[3] == (dt(year=2016, month=8, day=8), dt(year=2016, month=8, day=21))

        weeks = weeks_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)
        assert len(weeks) == 6
        logger.debug(weeks)
        logger.debug(weeks[0])
        assert weeks[0] == (dt(year=2016, month=7, day=4), dt(year=2016, month=7, day=10))
        assert weeks[1] == (dt(year=2016, month=7, day=11), dt(year=2016, month=7, day=17))
        assert weeks[2] == (dt(year=2016, month=7, day=18), dt(year=2016, month=7, day=24))
        assert weeks[3] == (dt(year=2016, month=7, day=25), dt(year=2016, month=7, day=31))
        assert weeks[4] == (dt(year=2016, month=8, day=1), dt(year=2016, month=8, day=7))
        assert weeks[5] == (dt(year=2016, month=8, day=8), dt(year=2016, month=8, day=14))

