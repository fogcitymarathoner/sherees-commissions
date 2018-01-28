from datetime import datetime as dt
import unittest

import reminders



class TestNextSemiMonth(unittest.TestCase):

    def test_first_half_dec(self):
        self.assertEqual( (dt(2017, 12, 16, 0, 0), dt(2017, 12, 31, 0, 0)),
                          reminders.next_semimonth(dt(2017, 12, 14), dt(2017, 12, 15)))

    def test_last_half_dec(self):
        self.assertEqual( (dt(2018, 1, 1, 0, 0), dt(2018, 1, 15, 0, 0)),
                          reminders.next_semimonth(dt(2017, 12, 16), dt(2017, 12, 31)))

    def test_first_half_jan(self):
        self.assertEqual( (dt(2017, 1, 16, 0, 0), dt(2017, 1, 31, 0, 0)),
                          reminders.next_semimonth(dt(2017, 1, 1), dt(2017, 1, 15)))

    def test_last_half_jan(self):
        self.assertEqual( (dt(2017, 2, 1, 0, 0), dt(2017, 2, 15, 0, 0)),
                          reminders.next_semimonth(dt(2017, 1, 16), dt(2017, 1, 31)))


if __name__ == '__main__':
    unittest.main()