"""Library routines for interacting with models"""
import hashlib
from datetime import datetime as dt

from s3_mysql_backup import YMD_FORMAT

from sqlalchemy import desc
from sqlalchemy import create_engine
from sqlalchemy import and_
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import false
from sqlalchemy.sql.expression import true

import api
from rrg import models
from rrg.lib import reminders as reminders_lib
from rrg.queries import periods

engine = create_engine("postgres://marc:flaming@localhost:5432/biz")
session = sessionmaker(bind=engine)
session = session()


def delete_vendor(obj_id):
    """Delete vendor in database."""

    session.delete(session.query(models.Vendor).get(obj_id))
    session.commit()


def delete_vendor_memo(obj_id):
    """Delete vendor in database."""

    session.delete(session.query(models.VendorMemo).get(obj_id))
    session.commit()


def delete_client(obj_id):
    """Delete vendor in database."""

    session.delete(session.query(models.Client).get(obj_id))
    session.commit()


def delete_client_memo(obj_id):
    """Delete vendor in database."""

    session.delete(session.query(models.ClientMemo).get(obj_id))
    session.commit()


def delete_expense(obj_id):
    """Delete expense in database."""

    session.delete(session.query(models.Expense).get(obj_id))
    session.commit()


def get_state_id(state_name):
    """Get state id from name"""

    state = session.query(models.State).filter(models.State.name == state_name).first()
    return state.id


def get_states():
    """Get list of states for drop down menu"""

    return {state.name: state.post_ab for state in
            session.query(models.State).order_by(models.State.id).all()}


def list_dropdown_expense_categories():
    """Get list of expense category dictionaries"""

    return {
        ec.name: ec.name for ec in session.query(
        models.ExpenseCategory).all()}


def list_page_clients(offset=0, page_size=30):
    """Get list of client dictionaries."""

    return [
        c.to_dict() for c in session.query(models.Client).order_by(
            desc(models.Client.modified_date)).limit(page_size).offset(offset)
        ]


def list_page_clients_memos(client_id, offset=0, page_size=30):
    """Get list of client memo dictionaries."""

    return [
        c.to_dict() for c in session.query(models.ClientMemo).filter(models.ClientMemo.client_id == client_id).order_by(
            desc(models.ClientMemo.modified_date)).limit(page_size).offset(offset)
        ]


def list_page_expenses(offset=0, page_size=30):
    """Get list of expenses dictionaries."""

    # fixme: this filter should be models.Expense.cleared is False, per lint
    return [
        c.to_dict() for c in session.query(models.Expense). \
            filter(models.Expense.cleared == false()). \
            order_by(desc(models.Expense.date)).limit(page_size).offset(offset)
        ]


def list_page_timecards(offset=0, page_size=30):
    """"""

    return [tc.to_dict() for tc in session.query(models.Invoice). \
        filter(models.Invoice.voided == false()). \
        filter(models.Invoice.posted == false()). \
        filter(models.Invoice.timecard == true()).limit(page_size).offset(offset)]


def list_page_vendors(offset=0, page_size=30):
    """"""

    return [vendor.to_dict() for vendor in session.query(models.Vendor).filter(models.Vendor.active).order_by(
        desc(models.Vendor.modified_date)).limit(30)
            ]


def list_page_vendors_memos(vendor_id, offset=0, page_size=30):
    """Get list of vendor memo dictionaries."""

    return [
        c.to_dict() for c in session.query(models.VendorMemo).filter(models.VendorMemo.vendor_id == vendor_id).order_by(
            desc(models.VendorMemo.modified_date)).limit(page_size).offset(offset)
        ]


def open_invoices():
    """
    return list of OPEN invoices
    """
    return [
        c.to_dict() for c in session.query(models.Invoice).filter(
            models.Invoice.voided == False,
            models.Invoice.posted == True,
            models.Invoice.cleared == False,
            models.Invoice.amount > 0)
        ]


def pastdue_invoices():
    """
    return list of PastDue invoices
    """

    res = []
    for oi in session.query(models.Invoice).filter(
                models.Invoice.voided == False,
                models.Invoice.posted == True,
                models.Invoice.cleared == False):
        if oi.duedate() <= dt.now() and \
                    oi.amount() > 0:
            res.append(oi.to_dict())
    return res


def save_client_check(payload):
    """

    :input: payload - json doc
    {'check': {'client_id': 0, date: '2017-01-01', 'notes': 'notes', 'number': 'number'},
     'payments': [{'invoice_id': 0, 'amount': 0, }]}
    :return:
    """
    client = None
    if payload['check']['client_id']:
        client = session.query(models.Client).get(payload['check']['client_id'])
    else:
        quit()
    if payload['check']['id']:
        check = session.query(models.ClientCheck).get(payload['check']['id'])
        check.payments.delete()
    else:
        check = models.ClientCheck()
    check.amount = sum([float(payment['amount']) for payment in payload['payments']])
    check.date = dt.strptime(payload['check']['date'], api.DATE_ISO_FORMAT)
    check.notes = payload['check']['notes']
    check.number = payload['check']['number']
    check.client = client
    if check.id is None:
        session.add(check)
        session.flush()
        session.commit()
    for pay in payload['payments']:
        invoice = session.query(models.Invoice).get(pay['invoice_id'])
        payment = models.InvoicePayment(check=check, invoice=invoice, amount=float(pay['amount']))
        if invoice.balance() == 0:
            invoice.cleared = True
        session.flush()
        session.add(payment)
        session.commit()


def save_client_memo(memo_dict):
    """"""

    if memo_dict['id'] > 0:
        memo = session.query(models.ClientMemo).get(memo_dict['id'])
        memo.notes = memo_dict['notes']
        memo.date = dt.strptime(memo_dict['date'], api.DATE_ISO_FORMAT)
    else:
        memo = models.ClientMemo(**memo_dict)
        memo.id = None
        session.add(memo)
    session.flush()
    session.commit()


def save_vendor_memo(memo_dict):
    """"""

    if memo_dict['id'] > 0:
        memo = session.query(models.VendorMemo).get(memo_dict['id'])
        memo.notes = memo_dict['notes']
        memo.date = dt.strptime(memo_dict['date'], api.DATE_ISO_FORMAT)
    else:
        memo = models.VendorMemo(**memo_dict)
        memo.id = None
        session.add(memo)
    session.flush()
    session.commit()


def save_timecard(timecard_dict):
    """"""

    print('saving %s' % timecard_dict)
    if timecard_dict['id']:
        timecard = session.query(models.Invoice).get(timecard_dict['id'])
        timecard.message = timecard_dict['message']
        timecard.notes = timecard_dict['notes']
        timecard.date = dt.strptime(timecard_dict['date'], api.DATE_ISO_FORMAT)
        timecard.period_start = dt.strptime(timecard_dict['period_start'], api.DATE_ISO_FORMAT)
        timecard.period_end = dt.strptime(timecard_dict['period_end'], api.DATE_ISO_FORMAT)
    else:
        timecard = models.Invoice(**timecard_dict)
        session.add(timecard)
    print(timecard)
    session.flush()
    session.commit()


def save_timecard_item(timecard_item_dict):
    """"""

    if timecard_item_dict['id']:
        titem = session.query(models.Iitem).get(timecard_item_dict['id'])
        titem.invoice_id = timecard_item_dict['invoice_id']
        titem.description = timecard_item_dict['description']
        titem.amount = timecard_item_dict['amount']
        titem.cost = timecard_item_dict['cost']
        titem.quantity = timecard_item_dict['quantity']
        titem.cleared = timecard_item_dict['cleared']
    else:
        titem = models.Iitem(**timecard_item_dict)
        session.add(titem)
    session.flush()
    session.commit()


def save_client(client_dict):
    """"""

    if client_dict['id'] > 0:
        client = session.query(models.Client).get(client_dict['id'])
    else:
        client = models.Client()
    client.name = client_dict['name']
    client.street1 = client_dict['street1']
    client.street2 = client_dict['street2']
    client.city = client_dict['city']
    client.state = session.query(models.State).get(get_state_id(client_dict['state']))
    client.zip = client_dict['zip']
    client.active = client_dict['active']
    client.terms = int(client_dict['terms'])
    if client_dict['id'] == 0:
        session.add(client)
    session.flush()
    session.commit()


def save_expense(expense_dict):
    """"""

    if expense_dict['id'] > 0:
        expense = session.query(models.Expense).get(expense_dict['id'])
    else:
        expense = models.Expense()
    expense.amount = float(expense_dict['amount'])
    expense.date = dt.strptime(expense_dict['date'], api.DATE_INPUT_FORMAT)
    expense.category = session.query(
        models.ExpenseCategory).filter(models.ExpenseCategory.name == expense_dict['category']).first()
    expense.description = expense_dict['description']
    if expense.employee_id is None:
        expense.employee = session.query(models.Employee).filter(models.Employee.firstname == 'MARC').first()
        print(expense.employee)
        expense.employee_id = expense.employee.id
    if expense_dict['id'] == 0:
        session.add(expense)
    session.flush()
    session.commit()


def save_vendor(vendor_dict):
    """"""

    if vendor_dict['id'] > 0:
        vendor = session.query(models.Vendor).get(vendor_dict['id'])
    else:
        vendor = models.Vendor()
    vendor.name = vendor_dict['name']
    vendor.purpose = vendor_dict['purpose']
    vendor.street1 = vendor_dict['street1']
    vendor.street2 = vendor_dict['street2']
    vendor.city = vendor_dict['city']
    vendor.state = session.query(models.State).get(get_state_id(vendor_dict['state']))
    vendor.zip = vendor_dict['zip']
    vendor.notes = vendor_dict['notes']
    vendor.active = vendor_dict['active']
    vendor.accountnumber = vendor_dict['accountnumber']
    vendor.apphone1 = vendor_dict['apphone1']
    vendor.apphone2 = vendor_dict['apphone2']
    vendor.apfirstname = vendor_dict['apfirstname']
    vendor.aplastname = vendor_dict['aplastname']
    vendor.secretbits = vendor_dict['secretbits']
    if vendor_dict['id'] == 0:
        session.add(vendor)
    session.flush()
    session.commit()


def search_clients(q_str, offset=0, page_size=30):
    """Search contacts."""

    return [cont.to_dict() for cont in session.query(models.Client).
        filter(or_(models.Client.street1.ilike('%' + q_str + '%'),
                   models.Client.street2.ilike('%' + q_str + '%'),
                   models.Client.city.ilike('%' + q_str + '%'),
                   models.Client.name.ilike('%' + q_str + '%'))).
        order_by(models.Client.name).limit(page_size).offset(offset)]


def search_expenses(q_str, offset=0, page_size=30):
    """Search expenses"""

    return [exp.to_dict() for exp in session. \
        query(models.Expense). \
        filter(and_(models.Expense.description.ilike('%%%s%%' % q_str))). \
        order_by(desc(models.Expense.date)).limit(page_size).offset(offset)]


def search_vendors(q_str, offset=0, page_size=30):
    """Search vendors"""

    return [vendor.to_dict() for vendor in session.query(models.Vendor).
        filter(or_(models.Vendor.name.ilike('%%%s%%' % q_str),
                   models.Vendor.purpose.ilike('%%%s%%' % q_str)
                   )).
        order_by(models.Vendor.name).limit(page_size).offset(offset)]


def set_invoice_posted(id, posted=True):
    """Sets invoices posted state"""

    invoice = session.query(models.Invoice).get(id)
    invoice.posted = posted
    session.commit()


def skip_contract_interval(contract_id, start, end):
    """

    :param contract_id:
    :param start: date string iso format
    :param end: date string iso format
    :return:
    """
    contract = session.query(models.Contract).get(contract_id)
    new_invoice = models.Invoice(
        contract=contract,
        period_start=start,
        period_end=end,
        timecard=True,
        date=dt.now(),
        terms=contract.terms,
        voided=True
    )
    session.add(new_invoice)
    session.commit()


def reminders(reminder_period_start, payroll_run_date, t_set, period):
    """
    generate list of reminders in a period for a period type [week, biweek, semimonth, month]
    :param session:
    :param reminder_period_start:
    :param payroll_run_date:
    :param t_set: set of hashes of DB records of past cards - timecard.contract.id, dt.strftime(timecard.period_start, YMD_FORMAT),
        dt.strftime(timecard.period_end, YMD_FORMAT)
    :param period:
    :return:
    """
    reminders_list = []
    weeks_of_inspection = weeks_between_dates(reminder_period_start, payroll_run_date)
    biweeks_of_inspection = biweeks_between_dates(reminder_period_start, payroll_run_date)
    semimonths_of_inspection = semimonths_between_dates(reminder_period_start, payroll_run_date)
    months_of_inspection = months_between_dates(reminder_period_start, payroll_run_date)
    for c, cl, em in contracts_per_period(session, period):
        if period == 'week':
            for ws, we in weeks_of_inspection:
                if reminder_hash(c, ws, we) not in t_set:
                    reminders_list.append((c, ws, we))
        elif period == 'biweek':
            for ws, we in biweeks_of_inspection:
                if reminder_hash(c, ws, we) not in t_set:
                    reminders_list.append((c, ws, we))
        elif period == 'semimonth':
            for ws, we in semimonths_of_inspection:
                if reminder_hash(c, ws, we) not in t_set:
                    reminders_list.append((c, ws, we))
        else:
            for ws, we in months_of_inspection:
                rh = reminder_hash(c, ws, we)
                if rh not in t_set:
                    reminders_list.append((c, ws, we))
    return reminders_list

def timecard_hash(timecard):
    """"""

    in_str = '%s %s %s' % (
        timecard.contract.id, dt.strftime(timecard.period_start, YMD_FORMAT),
        dt.strftime(timecard.period_end, YMD_FORMAT))
    return hashlib.sha224(in_str.encode('utf-8')).hexdigest()


def timecards():
    """
    returns set of timecard hashs of contract.id+startdate+enddate
    timecard not used
    :return:
    """

    with session.no_autoflush:
        return session.query(models.Invoice, models.Contract, models.Employee, models.Client).join(
            models.Contract).join(models.Employee).join(models.Client).filter(
            and_(models.Client.active == True, models.Contract.active == True,
                 models.Employee.active == True)).all()


def timecards_set():
    """"""

    timecards_set = set()
    for t in timecards():
        timecards_set.add(timecard_hash(t[0]))
    return timecards_set


def open_client_invoices(client_id):
    """"""

    open_invoices = []
    for inv, _ in \
          [contract for contract in session.query(
              models.Invoice, models.Contract).join(models.Invoice.contract).
                filter(models.Invoice.voided == false()). \
                filter(models.Invoice.cleared == false()).filter(
                    models.Contract.client_id == client_id)]:
        if inv.balance() > 0:
            open_invoices.append(inv.to_dict())
    return open_invoices


def contracts_per_period(session, period):
    """
    returns active contracts of period type - weekly, semimonthly, monthly
    and biweekly
    """
    if period not in periods:
        print('wrong period type')
    with session.no_autoflush:
        contracts = session.query(models.Contract, models.Client, models.Employee).join(models.Client) \
            .join(models.Employee).filter(
            and_(models.Contract.active == True, models.Client.active == True,
                 models.Employee.active == True,
                 models.Contract.period_id == periods[period])).all()
        return contracts


def biweeks_between_dates(start, end):
    """"""

    if start > end:
        print('biweek start date is greater than end date')
        return None
    biweek = reminders_lib.current_biweek(start)

    biweeks = [biweek]
    while biweek[1] < end:
        biweek = reminders_lib.next_biweek(*biweek)
        biweeks.append(biweek)

    return biweeks


def weeks_between_dates(start, end):
    """"""

    if start > end:
        print('week start date %s is greater than end date %s' % (start, end))
        return None
    week = reminders_lib.current_week(start)
    weeks = [week]
    while week[1] < end:
        week = reminders_lib.next_week(*week)
        weeks.append(week)
    return weeks


def months_between_dates(start, end):
    """"""

    if start > end:
        print('month start date is greater than end date')
        return None
    month = reminders_lib.current_month(start)

    months = [month]
    while month[1] < end:
        month = reminders_lib.next_month(*month)
        months.append(month)

    return months


def semimonths_between_dates(start, end):
    """"""

    if start > end:
        print('semimonth start date is greater than end date')
        return None
    semimonth = reminders_lib.current_semimonth(start)

    semimonths = [semimonth]
    while semimonth[1] < end:
        semimonth = reminders_lib.next_semimonth(*semimonth)
        semimonths.append(semimonth)

    return semimonths


def reminder_hash(contract, start, end):
    """
    from the point of view of contract generate hash for contract-pay-period
    :param contract:
    :param start:
    :param end:
    :return:
    """

    in_str = '%s %s %s' % (
        contract.id, dt.strftime(start, YMD_FORMAT),
        dt.strftime(end, YMD_FORMAT))
    return hashlib.sha224(in_str.encode('utf-8')).hexdigest()


def create_invoice_for_period(contract, period_start, period_end, date=None):
    """"""

    if not date:
        date = dt.now()
    new_inv = models.Invoice(contract_id=contract.id, period_start=period_start,
                             period_end=period_end, date=date,
                             employerexpenserate=.10, terms=contract.terms,
                             posted=False, prcleared=False, timecard=True,
                             cleared=False, timecard_receipt_sent=False,
                             message='Thank you for your business!', amount=0,
                             voided=False)
    session.add(new_inv)
    session.flush()
    for citem in contract.contract_items:
        new_iitem = models.Iitem(invoice_id=new_inv.id, description=citem.description,
                                 quantity=0.0, cleared=False,
                                 cost=citem.cost, amount=citem.amt)
        session.add(new_iitem)
        session.flush()
        for comm_item in citem.contract_comm_items:
            new_sales_comm_item = models.Citem(invoices_item_id=new_iitem.id,
                                               employee_id=comm_item.employee_id,
                                               percent=comm_item.percent,
                                               cleared=False, amount=0,
                                               description=new_iitem.description)
            session.add(new_sales_comm_item)
    session.commit()
    return new_inv
