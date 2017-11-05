import os
import re
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
from rrg.models import Expense
from rrg.models import ExpenseCategory
from rrg.models import Iitem
from rrg.models import Invoice
from rrg.models import InvoicePayment
from rrg.models import State
from rrg.models import User
from rrg.models import Vendor
from rrg.models import VendorMemo


from app import session

#
# Create User
#
user = User(firstname='Marc', lastname='Condon')
session.add(user)
session.flush()
quit()
#
# Expenses
#
sdir = os.path.join('datadir', 'biz', 'expenses')
print('Reading Expenses')
for dirName, subdirList, filelist in os.walk(sdir, topdown=False):
    print(filelist)
    for f in filelist:
        if re.search('\(2\)', f):
            print(f)
            continue
        exp = Expense()
        doc = ET.parse(os.path.join(sdir, f))
        exp.from_xml(doc)
        print(exp.category_id)
        cat = session.query(ExpenseCategory).get(exp.category_id)
        print(cat)
        exp.category = cat
        exp.employee_id = 1479
        session.add(exp)
        session.commit()

#
# Vendors
#
sdir = os.path.join('datadir', 'biz', 'vendors')
print('Reading Vendors')
for dirName, subdirList, filelist in os.walk(sdir, topdown=False):
    print(filelist)
    for f in filelist:
        if re.search('\(2\)', f):
            print(f)
            continue
        vendor = Vendor()
        doc = ET.parse(os.path.join(sdir, f))
        vendor.from_xml(doc)
        vendor.id = None
        vendor.created_user_id = user.id
        vendor.modified_user_id = user.id
        session.add(vendor)
        session.commit()
        session.flush()
        memos = doc.findall('memos')[0]
        for memo_ele in memos.findall('memo'):
            memo = VendorMemo()
            memo.vendor = vendor
            memo.from_xml(memo_ele)
            memo.id = None
            memo.created_user_id = user.id
            memo.modified_user_id = user.id
            session.add(memo)
            session.commit()
            session.flush()

for c in session.query(Vendor).all():
    print(c)
for c in session.query(VendorMemo):
    print(c)

session.commit()
