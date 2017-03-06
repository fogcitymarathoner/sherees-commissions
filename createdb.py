import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from sqlalchemy.orm import sessionmaker
import xml.etree.ElementTree as ET

from rrg.models import Base
from rrg.models import Client
from rrg.models import Contract
from rrg.models import ContractItem
from rrg.models import Employee
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
contractsx = []
for c in session.query(Employee):
    print(c)
for c in clientsx:
    f = os.path.join('datadir', 'biz', 'clients', c)
    if os.path.isfile(f):
        doc = ET.parse(f)
    else:
        print('problem with client file %s' % f)
        quit(1)
    print(doc.findall('name')[0].text)
    client = Client()
    client.from_xml(doc)
    client.created_user_id = user.id
    client.modified_user_id = user.id
    session.add(client)
    #
    # contracts
    #
    contracts = doc.findall('contracts')[0]
    for con_ele in contracts.findall('contract'):
        if int(con_ele.findall('employee_id')[0].text) == employee.id:
            print(employee.id)
            print(con_ele.findall('id')[0].text)
            contract = Contract()
            contract.from_xml(con_ele)
            session.add(contract)
            print('contract id %s' % contract.id)
            contractsx.append(contract.id)
            items = con_ele.findall('contract-items')[0]
            print(len(items))
            #
            #  contract items
            #
            print(ET.tostring(items))
            print(items.findall('contract-item'))
            for item_ele in items.findall('contract-item'):
                print(ET.tostring(item_ele))
                quit()
                print(item_ele.findall('id')[0].text)
                item = ContractItem()
                item.from_xml(item_ele)
                item.created_user_id = user.id
                item.modified_user_id = user.id
                session.add(item)

for c in session.query(Client):
    print(c)

session.commit()
