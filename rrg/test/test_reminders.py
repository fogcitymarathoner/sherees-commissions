import logging
import sys
from datetime import datetime as dt
from datetime import timedelta as td

from tabulate import tabulate

from rrg.helpers import date_to_datetime
from rrg.lib.reminders import biweeks_between_dates
from rrg.lib.reminders import current_semimonth
from rrg.lib.reminders import months_between_dates
from rrg.lib.reminders import semimonths_between_dates
from rrg.lib.reminders import weeks_between_dates
from rrg.lib.reminders_generation import forget_reminder
from rrg.lib.reminders_generation import reminders
from rrg.lib.reminders_generation import reminders_set
from rrg.lib.reminders_generation import timecard_hash
from rrg.lib.reminders_generation import timecards
from rrg.lib.reminders_generation import timecards_set
from rrg.models import Client
from rrg.models import Contract
from rrg.models import Employee
from rrg.models import Invoice
from rrg.models import is_pastdue
from rrg.models import periods
from rrg.models import session_maker
from rrg.queries import contracts_per_period

logging.basicConfig(filename='testing.log', level=logging.DEBUG)
logger = logging.getLogger('test')

logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


class Args(object):
    mysql_host = 'localhost'
    mysql_port = 3306
    db_user = 'root'
    db_pass = 'my_very_secret_password'
    db = 'rrg_test'


class Test:
    def setup_class(self):

        assert sys._called_from_test

        self.payroll_run_date = dt(year=2016, month=8, day=8)
        self.common_contract_start = dt(year=2016, month=7, day=1)
        logger.debug('Setup test reminders test')
        self.args = Args()

        self.session = session_maker(self.args)
        self.session.begin_nested()
        with self.session.no_autoflush:
            objects = []
            client_active = Client(name='weekly', active=True, terms=30)
            client_inactive = Client(name='weekly-inactive', active=False, terms=30)
            objects.append(client_active)
            objects.append(client_inactive)

            self.session.bulk_save_objects(objects)

            clients = self.session.query(Client).all()

            objects = []

            employee_active = Employee(firstname='firstname', lastname='lastname', active=True)
            employee_inactive = Employee(firstname='firstname', lastname='lastname', active=False)

            objects.append(employee_active)
            objects.append(employee_inactive)

            self.session.bulk_save_objects(objects)

            employees = self.session.query(Employee).all()

            logger.debug('employees[0]')
            logger.debug(employees[0])
            logger.debug('clients[0]')
            logger.debug(clients[0])

            objects = []

            # Active Contract
            objects.append(Contract(employee_id=employees[0].id, title='weekly-active-client-active-employee',
                                    client_id=clients[0].id, terms=clients[0].terms, active=True,
                                    period_id=periods['week'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id, title='biweekly-active-client-active-employee',
                                    client_id=clients[0].id, terms=clients[0].terms, active=True,
                                    period_id=periods['biweek'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id, title='semimonthly-active-client-active-employee',
                                    client_id=clients[0].id, terms=clients[0].terms, active=True,
                                    period_id=periods['semimonth'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[0].id, title='monthly-active-client-active-employee',
                                    client_id=clients[0].id, terms=clients[0].terms, active=True,
                                    period_id=periods['month'], startdate=self.common_contract_start))

            # Active Contracts Inactive Employees
            objects.append(Contract(employee_id=employees[1].id, title='weekly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, terms=clients[1].terms, active=True,
                                    period_id=periods['week'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='biweekly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, terms=clients[1].terms, active=True,
                                    period_id=periods['biweek'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='semimonthly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, terms=clients[1].terms, active=True,
                                    period_id=periods['semimonth'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='monthly-inactive-client-inactive-employee',
                                    client_id=clients[1].id, terms=clients[1].terms, active=True,
                                    period_id=periods['month'], startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id, client_id=clients[1].id, terms=clients[1].terms, active=False,
                         period_id=periods['week'], title='weekly-inactive',
                         startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id, title='biweekly-inactive', client_id=clients[1].id,
                         terms=clients[1].terms, active=False,
                         period_id=periods['biweek'], startdate=self.common_contract_start))

            objects.append(Contract(employee_id=employees[1].id, title='semimonthly-inactive', client_id=clients[1].id,
                                    terms=clients[1].terms,
                                    active=False,
                                    period_id=periods['semimonth'], startdate=self.common_contract_start))

            objects.append(
                Contract(employee_id=employees[1].id, title='monthly-inactive', client_id=clients[1].id,
                         terms=clients[1].terms, active=False,
                         period_id=periods['month'], startdate=self.common_contract_start))

            self.session.bulk_save_objects(objects)

            objects = []
            contracts = self.session.query(Contract).all()
            logger.debug('contracts')
            logger.debug(contracts[0].id)
            for contract in contracts:
                logger.debug(contract)

            weeks = weeks_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)
            second_week_start, second_week_end = weeks[1]

            objects.append(
                Invoice(contract_id=contracts[0].id, terms=contracts[0].terms, period_start=second_week_start.date(),
                        period_end=second_week_end.date(),
                        date=self.payroll_run_date.date()))

            objects.append(
                Invoice(contract_id=contracts[4].id, terms=contracts[4].terms, period_start=second_week_start.date(),
                        period_end=second_week_end.date(),
                        date=self.payroll_run_date.date()))
            objects.append(
                Invoice(contract_id=contracts[8].id, terms=contracts[8].terms, period_start=second_week_start.date(),
                        period_end=second_week_end.date(),
                        date=self.payroll_run_date.date()))

            biweeks = biweeks_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = biweeks[1]
            objects.append(Invoice(contract_id=contracts[1].id, terms=contracts[1].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[5].id, terms=contracts[5].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[9].id, terms=contracts[9].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))

            semimonths = semimonths_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = semimonths[1]
            objects.append(Invoice(contract_id=contracts[2].id, terms=contracts[2].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[6].id, terms=contracts[6].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[10].id, terms=contracts[10].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))

            months = months_between_dates(dt(year=2016, month=7, day=4), self.payroll_run_date)

            start, end = months[1]
            objects.append(Invoice(contract_id=contracts[3].id, terms=contracts[3].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[7].id, terms=contracts[7].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            objects.append(Invoice(contract_id=contracts[11].id, terms=contracts[11].terms, period_start=start.date(),
                                   period_end=end.date(),
                                   date=self.payroll_run_date.date()))
            self.session.bulk_save_objects(objects)

            for i in self.session.query(Invoice).all():
                logger.debug(i)
            months_between_dates(self.payroll_run_date, self.payroll_run_date)

            current_semimonth(dt(year=self.payroll_run_date.year, month=self.payroll_run_date.month, day=16))

            assert not weeks_between_dates(self.payroll_run_date + td(days=1), self.payroll_run_date)

    def teardown_class(self):
        logger.debug('Teardown reminders')
        self.session.rollback()
        self.session.flush()

    def test_in_test(self):
        """
        test _called_from_test
        :return:
        """
        assert sys._called_from_test

    def test_due_date_pastdue(self, capsys):
        """
        test invoice due date calculation
        """
        logger.debug('testing duedate')
        first_inv = self.session.query(Invoice).all()[0]
        logger.debug(first_inv)
        assert first_inv.duedate() == dt(year=2016, month=9, day=7)
        assert is_pastdue(first_inv, date=dt(year=2016, month=9, day=6))
        logger.debug(is_pastdue(first_inv))

        assert not is_pastdue(first_inv, date=dt(year=2016, month=9, day=8))

    def test_models(self, capsys):
        """
        test model interactions
        """
        logger.debug('testing models')
        self.args.period = 'week'
        contracts_w = contracts_per_period(self.session, self.args)

        logger.debug('employees')
        logger.debug(self.session.query(Employee).all())
        logger.debug('contracts')
        logger.debug(contracts_w)
        #
        for contract, client, employee in contracts_w:
            logger.debug('contract - %s' % contract)
            logger.debug('client - %s' % client)
            logger.debug('employee - %s' % employee)

        assert 1 == len(contracts_w)

        self.args.period = 'biweek'
        contracts_b = contracts_per_period(self.session, self.args)
        assert 1 == len(contracts_b)

        self.args.period = 'semimonth'
        contracts_s = contracts_per_period(self.session, self.args)
        assert 1 == len(contracts_s)

        self.args.period = 'month'
        contracts_m = contracts_per_period(self.session, self.args)
        assert 1 == len(contracts_m)

    def test_reminders(self, capsys):
        """
        test model interactions
        """
        logger.debug('testing reminders')

        self.args.payroll_run_date = self.payroll_run_date
        r_set = reminders_set(self.session, self.args)
        tbl = []
        tcards = timecards(self.session, self.args)
        t_set = timecards_set(self.session, self.args)
        logger.debug('timecards')
        for t in tcards:
            tbl.append([t[0].id, t[0].period_start, t[0].period_end, t[1].active, t[1].title, t[2].active, t[3].active,
                        1 if timecard_hash(t[0]) in r_set else 0,
                        timecard_hash(t[0])])
        logger.debug(tabulate(tbl,
                              headers=['id', 'start', 'end', 'contract-active', 'contract-title', 'employee-active',
                                       'client-active', 'already-has-reminder', 'timecard-hash']))
        # weekly
        logger.debug('weekly')
        assert dt(year=2016, month=7, day=11) == date_to_datetime(tcards[0][0].period_start)
        assert dt(year=2016, month=7, day=17) == date_to_datetime(tcards[0][0].period_end)
        assert True is tcards[0][1].active
        assert True is tcards[0][2].active
        assert True is tcards[0][3].active
        # second weekly
        logger.debug('biweekly')
        assert dt(year=2016, month=7, day=11) == date_to_datetime(tcards[1][0].period_start)
        assert dt(year=2016, month=7, day=24) == date_to_datetime(tcards[1][0].period_end)
        assert True is tcards[1][1].active
        assert True is tcards[1][2].active
        assert True is tcards[1][3].active
        # biweekly
        assert dt(year=2016, month=7, day=16) == date_to_datetime(tcards[2][0].period_start)
        assert dt(year=2016, month=7, day=31) == date_to_datetime(tcards[2][0].period_end)
        assert True is tcards[2][1].active
        assert True is tcards[2][2].active
        assert True is tcards[2][3].active
        # monthly
        assert dt(year=2016, month=8, day=1) == date_to_datetime(tcards[3][0].period_start)
        # monthly
        assert dt(year=2016, month=8, day=31) == date_to_datetime(tcards[3][0].period_end)
        # invoice
        assert True is tcards[3][1].active
        # contract
        assert True is tcards[3][2].active
        # employee
        assert True is tcards[3][3].active

        logger.debug('biweekly')
        self.args.period = 'biweek'
        for c, ws, we in reminders(self.session, self.payroll_run_date - td(days=30), self.payroll_run_date, t_set,
                                   self.args):
            logger.debug('%s %s %s' % (c, ws, we))
        logger.debug('semimonthly')
        self.args.period = 'semimonth'
        for c, ws, we in reminders(self.session, self.payroll_run_date - td(days=30), self.payroll_run_date, t_set,
                                   self.args):
            logger.debug('%s %s %s' % (c, ws, we))
        logger.debug('monthly')
        self.args.period = 'month'
        for c, ws, we in reminders(self.session, self.payroll_run_date - td(days=30), self.payroll_run_date, t_set,
                                   self.args):
            logger.debug('%s %s %s' % (c, ws, we))

        self.args.period = 'week'
        reminders_to_be_sent = reminders(self.session, self.payroll_run_date - td(days=30), self.payroll_run_date,
                                         t_set, self.args)

        # weekly

        logger.debug('weekly')
        for c, ws, we in reminders_to_be_sent:
            logger.debug('%s %s %s' % (c, ws, we))

        assert dt(year=2016, month=7, day=4) == reminders_to_be_sent[0][1]
        assert dt(year=2016, month=7, day=10) == reminders_to_be_sent[0][2]
        assert True is reminders_to_be_sent[0][0].active
        assert True is reminders_to_be_sent[0][0].employee.active
        assert True is reminders_to_be_sent[0][0].client.active

        # skipped 7/11 - 7/17
        assert dt(year=2016, month=7, day=18) == reminders_to_be_sent[1][1]
        assert dt(year=2016, month=7, day=24) == reminders_to_be_sent[1][2]
        assert True is reminders_to_be_sent[1][0].active
        assert True is reminders_to_be_sent[1][0].employee.active
        assert True is reminders_to_be_sent[1][0].client.active

        # biweekly

        self.args.period = 'biweek'
        reminders_to_be_sent = reminders(self.session, self.payroll_run_date - td(days=30), self.payroll_run_date,
                                         t_set, self.args)
        assert dt(year=2016, month=6, day=27) == reminders_to_be_sent[0][1]
        assert dt(year=2016, month=7, day=10) == reminders_to_be_sent[0][2]
        assert True is reminders_to_be_sent[0][0].active
        assert True is reminders_to_be_sent[0][0].employee.active
        assert True is reminders_to_be_sent[0][0].client.active

        # skipped 7/11 - 7/24

        assert dt(year=2016, month=7, day=25) == reminders_to_be_sent[1][1]
        assert dt(year=2016, month=8, day=7) == reminders_to_be_sent[1][2]
        assert True is reminders_to_be_sent[1][0].active
        assert True is reminders_to_be_sent[1][0].employee.active
        assert True is reminders_to_be_sent[1][0].client.active

        # semimonthly
        self.args.period = 'semimonth'
        reminders_to_be_sent = reminders(self.session, self.payroll_run_date - td(days=30), self.payroll_run_date,
                                         t_set, self.args)
        assert dt(year=2016, month=7, day=1) == reminders_to_be_sent[0][1]
        assert dt(year=2016, month=7, day=15) == reminders_to_be_sent[0][2]
        assert True is reminders_to_be_sent[0][0].active
        assert True is reminders_to_be_sent[0][0].employee.active
        assert True is reminders_to_be_sent[0][0].client.active

        # skipped 7/15 - 7/31
        assert dt(year=2016, month=8, day=1) == reminders_to_be_sent[1][1]
        assert dt(year=2016, month=8, day=15) == reminders_to_be_sent[1][2]
        assert True is reminders_to_be_sent[1][0].active
        assert True is reminders_to_be_sent[1][0].employee.active
        assert True is reminders_to_be_sent[1][0].client.active

        # monthly

        self.args.period = 'month'
        reminders_to_be_sent = reminders(self.session, self.payroll_run_date - td(days=30), self.payroll_run_date,
                                         t_set, self.args)
        assert dt(year=2016, month=7, day=1) == reminders_to_be_sent[0][1]
        assert dt(year=2016, month=7, day=31) == reminders_to_be_sent[0][2]
        assert True is reminders_to_be_sent[0][0].active
        assert True is reminders_to_be_sent[0][0].employee.active
        assert True is reminders_to_be_sent[0][0].client.active
        # Second month missing
        assert 1 == len(reminders_to_be_sent)

        for r in reminders_to_be_sent:
            logger.debug(r)

    def test_reminder_forgetting(self, capsys):
        """
        test forgetting a model
        """
        logger.debug('testing reminder forgetting, week')
        ####

        self.args.payroll_run_date = self.payroll_run_date
        self.args.period = 'week'
        r_set = reminders_set(self.session, self.args)
        tbl = []
        tcards = timecards(self.session, self.args)
        t_set = timecards_set(self.session, self.args)
        logger.debug('All timecards ever submitted')
        for t in tcards:
            tbl.append([t[0].id, t[0].period_start, t[0].period_end, t[1].active, t[1].title, t[2].active, t[3].active,
                        1 if timecard_hash(t[0]) in r_set else 0,
                        timecard_hash(t[0])])
        logger.debug(tabulate(tbl,
                              headers=['id', 'start', 'end', 'contract-active', 'contract-title', 'employee-active',
                                       'client-active', 'already-has-reminder', 'timecard-hash']))

        # Reminder outstanding presented to user for selection
        self.args.period = 'week'
        week_reminders_to_be_sent = reminders(self.session, self.payroll_run_date - td(days=30), self.payroll_run_date,
                                         t_set, self.args)
        contract_of_forgotten_reminder = week_reminders_to_be_sent[0][0]
        logger.debug('Pending Week Reminders BEFORE forgetting first reminder')
        tbl = []
        for r in week_reminders_to_be_sent:
            # conract, start, end = t
            tbl.append([r[0].id, r[0].title, '%s %s' % (r[0].employee.firstname, r[0].employee.lastname), r[1], r[2]])
        logger.debug(tabulate(tbl, headers=['id', 'title', 'employee', 'start', 'end']))
        assert 5 == len(week_reminders_to_be_sent)
        self.args.number = 1
        logger.debug('Forgetting first reminder')
        forget_reminder(self.session, self.payroll_run_date - td(days=30), dt.now(), t_set, self.args)

        t_set = timecards_set(self.session, self.args)
        self.args.period = 'week'
        week_reminders_to_be_sent = reminders(self.session, self.payroll_run_date - td(days=30), self.payroll_run_date,
                                         t_set, self.args)
        logger.debug('Pending Week Reminders AFTER forgetting first reminder')
        tbl = []
        for r in week_reminders_to_be_sent:
            tbl.append([r[0].id, r[0].title, '%s %s' % (r[0].employee.firstname, r[0].employee.lastname), r[1], r[2]])
        logger.debug(tabulate(tbl, headers=['id', 'title', 'employee', 'start', 'end']))
        assert 4 == len(week_reminders_to_be_sent)
        # former second reminder is current first reminder, first reminder forgotten
        assert dt(2016, 7, 18) == week_reminders_to_be_sent[0][1]
        assert dt(2016, 7, 24) == week_reminders_to_be_sent[0][2]
        invs = self.session.query(Invoice).all()
        last_inv = invs[len(invs)-1:len(invs)][0]
        logger.debug(last_inv)
        logger.debug(last_inv.period_start)
        assert contract_of_forgotten_reminder == last_inv.contract
        assert date_to_datetime(last_inv.period_start) == dt(2016, 7, 4)
        assert date_to_datetime(last_inv.period_end) == dt(2016, 7, 10)
        assert last_inv.voided == True
