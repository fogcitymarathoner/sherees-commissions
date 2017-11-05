from datetime import datetime as dt
import marshmallow

DATE_INPUT_FORMAT = '%m/%d/%Y'
DATE_ISO_FORMAT = '%Y-%m-%d'
def formatted_list_client_line(client_dict):
    """"""

    line = '%s %s %s %s %s' % (
        client_dict['id'],
        client_dict['name'],
        client_dict['city'],
        client_dict['state'],
        client_dict['created_date'],  # .strftime(tk_forms.DATE_OUTPUT_READABLE_FORMAT)
    )
    return line

def formatted_list_expense_line(expense_dict):
    """"""

    line = '%s %s %s %s %s %s %s' % (
        expense_dict['id'],
        expense_dict['date'].strftime(DATE_INPUT_FORMAT),
        expense_dict['amount'],
        expense_dict['category'],
        expense_dict['description'],
        expense_dict['notes'],
        expense_dict['created_date'].strftime(DATE_INPUT_FORMAT),
    )
    return line


def formatted_list_invoice_line(invoice_dict):
    """"""

    def invoice_amount_dict(invoice_dict):
        """"""

        amount = 0
        for item in invoice_dict['invoice_items']:
            amount += float(item['amount']) * float(item['quantity'])
        return amount

    return '%s %s %s %s %s start: %s end: %s  amount: %s ' % (
        invoice_dict['id'],
        dt.strptime(invoice_dict['date'], DATE_ISO_FORMAT).strftime(DATE_INPUT_FORMAT),
        invoice_dict['contract']['client']['name'],
        invoice_dict['contract']['employee']['first'],
        invoice_dict['contract']['employee']['last'],
        dt.strptime(invoice_dict['period_start'], DATE_ISO_FORMAT).strftime(DATE_INPUT_FORMAT),
        dt.strptime(invoice_dict['period_end'], DATE_ISO_FORMAT).strftime(DATE_INPUT_FORMAT),
        invoice_amount_dict(invoice_dict),
    )

def formatted_list_timecard_line(timecard_dict):
    """Format contact for UI list interface."""

    return '%s %s %s %s %s %s %s ' % (
        timecard_dict['id'],
        timecard_dict['contract']['client']['name'],
        timecard_dict['contract']['employee']['first'],
        timecard_dict['contract']['employee']['last'],
        timecard_dict['date'],
        dt.strptime(timecard_dict['period_start'], DATE_ISO_FORMAT).strftime(DATE_INPUT_FORMAT),
        timecard_dict['period_end']
    )

def formatted_list_vendor_line(vendor_dict):
    """"""

    return '%s %s %s %s %s %s  modified: %s created: %s' % (
        vendor_dict['id'],
        vendor_dict['name'],
        vendor_dict['purpose'],
        vendor_dict['apphone1'],
        vendor_dict['city'],
        vendor_dict['state'],
        vendor_dict['modified_date'],
        vendor_dict['created_date']
    )


class Check(object):
    # pylint: disable=too-few-public-methods
    """Client Check Data Shadowing AppletWriteCheck Elements"""

    def __init__(self, id=0,  # pylint: disable=redefined-builtin
                 client_id=0,
                 notes=None, number=None, date=None):
        """"""
        self.id = id  # pylint: disable=invalid-name
        self.client_id = client_id
        self.date = date
        self.notes = notes
        self.number = number


class Client(object):
    """"""

    def __init__(self, id=0, client_id=0, name='',
                 street1='', street2='', city='', state='', zip='',
                 terms=30, active=True, modified_date='2017-01-01', created_date='2017-01-01',
                 memos=[]):
        """"""

        self.id = id
        self.client_id = client_id
        self.name = name
        self.street1 = street1
        self.street2 = street2
        self.city = city
        self.state = state
        self.zip = zip
        self.terms = terms
        self.active = active
        self.modified_date = modified_date
        self.created_date = created_date
        self.memos = [ ClientMemo(**memo) for memo in memos]

    def to_dict(self):
        """"""

        return {
            'id': self.id,
            'name': self.name,
            'street1': self.street1,
            'street2': self.street2,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'terms': self.terms,
            'active': self.active,
            'modified_date': self.modified_date,
            'created_date': self.created_date,
        }


class ClientSchema(marshmallow.Schema):
    """"""

    id = marshmallow.fields.Int()  # pylint: disable=invalid-name
    name = marshmallow.fields.Str()
    street1 = marshmallow.fields.Str()
    street2 = marshmallow.fields.Str()
    city = marshmallow.fields.Str()
    state = marshmallow.fields.Str()
    zip = marshmallow.fields.Str()
    terms = marshmallow.fields.Int()
    message = marshmallow.fields.Str()
    active = marshmallow.fields.Bool()
    modified_date = marshmallow.fields.Date()
    created_date = marshmallow.fields.Date()

    @marshmallow.post_load
    def make_post(self, data):  # pylint: disable=no-self-use
        """"""

        return Client(**data)


class ClientMemo(object):
    # pylint: disable=too-few-public-methods
    """Memo Data Shadowing AppletFormMemoEdit/Create Elements"""

    def __init__(self, id=0,  # pylint: disable=redefined-builtin
                 client_id=0,
                 notes=None, date=None, modified_date=None, created_date=None):
        """"""
        self.id = id  # pylint: disable=invalid-name
        self.client_id = client_id
        self.notes = notes
        self.date = date
        self.modified_date = dt.strptime(
            modified_date, DATE_INPUT_FORMAT) if modified_date else dt.now()
        self.created_date = dt.strptime(
            created_date, DATE_INPUT_FORMAT) if created_date else dt.now()

    def set_notes(self, notes):
        """"""

        self.notes = notes

    def set_date(self, date):
        """"""

        self.date = date

    def to_dict(self):
        """"""
        return {
            'id': self.id,
            'client_id': self.client_id,
            'notes': self.notes,
            'date': self.date.strftime(DATE_ISO_FORMAT),
        }


class ClientMemoSchema(marshmallow.Schema):
    """"""

    id = marshmallow.fields.Int()  # pylint: disable=invalid-name
    client_id = marshmallow.fields.Int()
    name = marshmallow.fields.Str()
    content = marshmallow.fields.Str()
    notes = marshmallow.fields.Str()
    secretbits = marshmallow.fields.Str()
    tags_string = marshmallow.fields.Str()
    date = marshmallow.fields.Date()
    created_date = marshmallow.fields.Date()
    modified_date = marshmallow.fields.Date()

    @marshmallow.post_load
    def make_memo(self, data):  # pylint: disable=no-self-use
        """"""

        return ClientMemo(**data)


class Contract(object):
    """"""

    def __init__(self, id=0, title='Professional IT Services',
                 notes='', client={}, employee={}, startdate='0000-00-00', enddate='0000-00-00'):
        """"""

        self.id = id
        self.title = title
        self.notes = notes
        self.client = Client(**client)
        self.employee = Employee(**employee)
        self.startdate = startdate
        self.enddate = enddate


class Employee(object):
    """"""

    def __init__(self, id=0,
                 first='', last='', startdate='0000-00-00', enddate='0000-00-00'):
        """"""

        self.id = id
        self.first = first
        self.last = last
        self.startdate = startdate
        self.enddate = enddate


class Expense(object):
    # pylint: disable=too-few-public-methods
    """Expense Data Shadowing AppletFormExpense Elements"""

    def __init__(self,
                 id=0,  # pylint: disable=redefined-builtin
                 category=None,
                 amount=None, date=None, description=None, notes=None,
                 created_date=None, modified_date=None):
        self.id = id  # pylint: disable=invalid-name
        self.category = category
        self.amount = amount
        self.date = date
        self.created_date = created_date
        self.modified_date = modified_date
        self.notes = notes
        self.description = description


    def to_dict(self):
        """"""

        return {
            'id': self.id,
            'category': self.category,
            'amount': self.amount,
            'notes': self.notes,
            'description': self.description,
            'date': self.date,
            'modified_date': self.modified_date.strftime(DATE_ISO_FORMAT),
            'created_date': self.created_date.strftime(DATE_ISO_FORMAT),
        }


class ExpenseSchema(marshmallow.Schema):
    """"""

    id = marshmallow.fields.Int()  # pylint: disable=invalid-name
    category = marshmallow.fields.Str()
    notes = marshmallow.fields.Str()
    amount = marshmallow.fields.Float()
    date = marshmallow.fields.Date()
    created_date = marshmallow.fields.Date()
    modified_date = marshmallow.fields.Date()
    description = marshmallow.fields.Str()


class InvoiceItem(object):
    """"""

    def __init__(self, id=0,
                 invoice_id=0, description='', amount=0.0, cost=0.0, quantity=0.0, cleared=False):
        """"""

        self.id = id
        self.invoice_id = invoice_id
        self.description = description
        self.amount = amount
        self.cost = cost
        self.quantity = quantity
        self.cleared = cleared

    def __repr__(self):
        return "<InvoiceItem(id: '%s', invoice_id: '%s', description: '%s', amount='%s', cost='%s', quantity='%s)" % \
               (self.id, self.invoice_id, self.description, self.amount, self.cost, self.quantity)

    def to_dict(self):
        """"""

        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'description': self.description,
            'amount': self.amount,
            'cost': self.cost,
            'quantity': self.quantity,
            'cleared': self.cleared,
        }


class InvoiceItemSchema(marshmallow.Schema):
    """"""

    id = marshmallow.fields.Int()  # pylint: disable=invalid-name

    invoice_id = marshmallow.fields.Int()
    description = marshmallow.fields.Str()
    amount = marshmallow.fields.Float()
    cost = marshmallow.fields.Float()
    quantity = marshmallow.fields.Float()
    cleared = marshmallow.fields.Bool()

    @marshmallow.post_load
    def make_post(self, data):  # pylint: disable=no-self-use
        """"""

        return InvoiceItem(**data)


class InvoicePayment(object):
    """"""

    def __init__(self, id=0):
        """"""

        self.id = id


class Timecard(object):
    """"""

    def __init__(self, id=0, contract={}, employee={},
                 date='0000-00-00', period_start='0000-00-00', period_end='0000-00-00',
                 posted=False, cleared=False, voided=False, prcleared=False, message='Thank you for your business!',
                 invoice_items=[], invoice_payments=[], balance=0.0,
                 po='',
                 employerexpenserate=0.0,
                 terms=30,
                 timecard=True,
                 notes=''
                 ):
        """"""

        self.id = id
        self.balance = balance
        self.contract = Contract(**contract)
        self.employee = Employee(**employee)
        self.date = date
        self.period_start = period_start
        self.period_end = period_end
        self.posted = posted
        self.cleared = cleared
        self.voided = voided
        self.prcleared = prcleared
        self.message = message
        self.notes = notes
        self.invoice_items = [InvoiceItem(**invoice_item) for invoice_item in invoice_items]
        self.invoice_payments = [InvoicePayment(**invoice_payment) for invoice_payment in invoice_payments]

    def __repr__(self):
        invoice_items = ''
        for i in self.invoice_items:
            invoice_items += i.__repr__() + ','

        return "<Timecard(id: '%s', date: '%s', period_start: '%s', period_end='%s', invoice_items='[%s]')" % (
            self.id, self.date, self.period_start, self.period_end, invoice_items)


    def set_date(self, date):
        """"""

        self.date= date

    def set_message(self, message):
        """"""

        self.message = message

    def set_notes(self, notes):
        """"""

        self.notes = notes

    def set_period_start(self, period_start):
        """"""

        self.period_start = period_start

    def set_period_end(self, period_end):
        """"""

        self.period_end = period_end

    def to_dict(self):
        """"""
        return {
            'id': self.id,
            'message': self.message,
            'notes': self.notes,
            'date': self.date,
            'period_start': self.period_start,
            'period_end': self.period_end,
        }


class TimecardSchema(marshmallow.Schema):
    """"""

    id = marshmallow.fields.Int()  # pylint: disable=invalid-name
    date = marshmallow.fields.Date()
    period_start = marshmallow.fields.Date()
    period_end = marshmallow.fields.Date()
    message = marshmallow.fields.Str()
    notes = marshmallow.fields.Str()

    @marshmallow.post_load
    def make_post(self, data):  # pylint: disable=no-self-use
        """"""

        return Timecard(**data)


class Vendor(object):
    """"""

    def __init__(self, id=0,
                 name='',
                 purpose='',
                 street1='',
                 street2='',
                 city='',
                 state='',
                 zip='',
                 notes='',
                 active='',
                 accountnumber='',
                 apphone1='',
                 apphone2='',
                 apfirstname='',
                 aplastname='',
                 secretbits='',
                 created_date='',
                 modified_date='',
                 memos=[],
                 ):
        """"""

        self.id = id
        self.name = name
        self.purpose = purpose
        self.street1 = street1
        self.street2 = street2
        self.city = city
        self.state = state
        self.zip = zip
        self.notes = notes
        self.active = active
        self.accountnumber = accountnumber
        self.apphone1 = apphone1
        self.apphone2 = apphone2
        self.apfirstname = apfirstname
        self.aplastname = aplastname
        self.secretbits = secretbits
        self.created_date = created_date
        self.modified_date = modified_date
        self.memos = [ VendorMemo(**memo) for memo in memos]

    def to_dict(self):
        """"""

        return {
            'id': self.id,
            'name': self.name,
            'purpose': self.purpose,
            'street1': self.street1,
            'street2': self.street2,
            'city': self.city,
            'state': self.state,
            'zip': self.zip,
            'notes': self.notes,
            'active': self.active,
            'accountnumber': self.accountnumber,
            'apphone1': self.apphone1,
            'apphone2': self.apphone2,
            'apfirstname': self.apfirstname,
            'aplastname': self.aplastname,
            'secretbits': self.secretbits,
        }

class VendorSchema(marshmallow.Schema):
    """"""

    id = marshmallow.fields.Int()  # pylint: disable=invalid-name
    name = marshmallow.fields.Str()
    purpose = marshmallow.fields.Str()
    street1 = marshmallow.fields.Str()
    street2 = marshmallow.fields.Str()
    city = marshmallow.fields.Str()
    state = marshmallow.fields.Str()
    zip = marshmallow.fields.Str()
    notes = marshmallow.fields.Str()
    active = marshmallow.fields.Bool()
    accountnumber = marshmallow.fields.Str()
    apphone1 = marshmallow.fields.Str()
    apphone2 = marshmallow.fields.Str()
    apfirstname = marshmallow.fields.Str()
    aplastname = marshmallow.fields.Str()
    secretbits = marshmallow.fields.Str()

    @marshmallow.post_load
    def make_post(self, data):  # pylint: disable=no-self-use
        """"""

        return Vendor(**data)


class VendorMemo(object):
    # pylint: disable=too-few-public-methods
    """Memo Data Shadowing AppletFormMemoEdit/Create Elements"""

    def __init__(self, id=0,  # pylint: disable=redefined-builtin
                 vendor_id=0,
                 notes=None, date=None, modified_date=None, created_date=None):
        """"""

        self.id = id  # pylint: disable=invalid-name
        self.vendor_id = vendor_id
        self.notes = notes
        self.date = date
        self.modified_date = dt.strptime(
            modified_date, DATE_ISO_FORMAT) if modified_date else dt.now()
        self.created_date = dt.strptime(
            created_date, DATE_ISO_FORMAT) if created_date else dt.now()

    def set_notes(self, notes):
        """"""

        self.notes = notes

    def set_date(self, date):
        """"""

        self.date = date

    def to_dict(self):
        """"""
        return {
            'id': self.id,
            'vendor_id': self.vendor_id,
            'notes': self.notes,
            'date': self.date,
        }


class VendorMemoSchema(marshmallow.Schema):
    """"""

    id = marshmallow.fields.Int()  # pylint: disable=invalid-name
    vendor_id = marshmallow.fields.Int()
    notes = marshmallow.fields.Str()
    date = marshmallow.fields.Date()
    created_date = marshmallow.fields.Date()
    modified_date = marshmallow.fields.Date()

    @marshmallow.post_load
    def make_memo(self, data):  # pylint: disable=no-self-use
        """"""

        return VendorMemo(**data)
