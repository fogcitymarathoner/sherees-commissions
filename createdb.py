import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from sqlalchemy.orm import sessionmaker
import xml.etree.ElementTree as ET

from rrg.models import Base
from rrg.models import Client
from rrg.models import ClientCheck
from rrg.models import ClientManager
from rrg.models import ClientMemo
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.models import Employee
from rrg.models import Invoice
from rrg.models import State
from rrg.models import User

engine = create_engine("postgres://postgres:mysecretpassword@192.168.99.100:32770/biz")

session = sessionmaker(bind=engine)
session = session()

if not database_exists(engine.url):
    create_database(engine.url)

print(database_exists(engine.url))

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
#
# Create User
#
user = User(firstname='Marc', lastname='Condon')
session.add(user)
#
# States
#
sdir = os.path.join('datadir', 'biz', 'states')

for dirName, subdirList, filelist in os.walk(sdir, topdown=False):
    for f in filelist:
        state = State()
        doc = ET.parse(os.path.join('datadir', 'biz', 'states', f))
        state.created_user_id = user.id
        state.modified_user_id = user.id
        state.from_xml(doc)
        session.add(state)

for c in session.query(State):
    print(c)
#
# Employee
#
f = os.path.join('datadir', 'biz', 'employees', '01479.xml')
print(f)

if os.path.isfile(f):
    doc = ET.parse(f)
else:
    print('%s not arround cannot import employee')
    quit(1)

doc = ET.parse(os.path.join(f))
employee = Employee()
employee.from_xml(doc)
employee.created_user_id = user.id
employee.modified_user_id = user.id
session.add(employee)

#
# Clients
#
clientsx = ['00062.xml', '00116.xml', '00185.xml']
# collect list of contracts for selecting transactions
#contractsx = []
for c in session.query(Employee):
    print(c)
for c in clientsx:
    f = os.path.join('datadir', 'biz', 'clients', c)
    if os.path.isfile(f):
        doc = ET.parse(f)
    else:
        print('problem with client file %s' % f)
        quit(1)

    client = Client()
    client.from_xml(doc)
    client.created_user_id = user.id
    client.modified_user_id = user.id
    session.add(client)
    memos = doc.findall('memos')[0]
    for memo_ele in memos.findall('memo'):
        memo = ClientMemo()
        memo.from_xml(memo_ele)
        memo.created_user_id = user.id
        memo.modified_user_id = user.id
        session.add(memo)

    managers = doc.findall('managers')[0]
    for man_ele in managers.findall('manager'):
        manager = ClientManager()
        manager.from_xml(man_ele)
        manager.created_user_id = user.id
        manager.modified_user_id = user.id
        session.add(manager)
    #
    # checks
    #
    checks = doc.findall('checks')[0]
    for ck_ele in checks.findall('check'):
        check = ClientCheck()
        check.from_xml(ck_ele)
        check.created_user_id = user.id
        check.modified_user_id = user.id
        session.add(check)
    #
    # contracts
    #
    contracts = doc.findall('contracts')[0]
    for con_ele in contracts.findall('contract'):
        if int(con_ele.findall('employee_id')[0].text) == employee.id:
            contract = Contract()
            contract.from_xml(con_ele)
            contract.created_user_id = user.id
            contract.modified_user_id = user.id
            session.add(contract)

            #contractsx.append(contract.id)
            items = con_ele.findall('contract-items')[0]

            #
            #  contract items
            #
            for item_ele in items.findall('contract-item'):

                item = ContractItem()
                item.from_xml(item_ele)
                item.created_user_id = user.id
                item.modified_user_id = user.id
                session.add(item)

            invoices = con_ele.findall('invoices')[0]
            #
            # invoices
            #
            for invoice_ele in invoices.findall('invoice'):
                invoice = Invoice()
                invoice.from_xml(invoice_ele)
                invoice.created_user_id = user.id
                invoice.modified_user_id = user.id
                session.add(invoice)

for c in session.query(Client):
    print(c)
for c in session.query(ContractItem):
    print(c)
for c in session.query(ClientCheck):
    print(c)

session.commit()
