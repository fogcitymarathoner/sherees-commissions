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
from rrg.models import Iitem
from rrg.models import State
from rrg.models import User
from rrg.models import Vendor
from rrg.models import VendorMemo

engine = create_engine("postgres://postgres:mysecretpassword@192.168.99.100:32771/biz")

session = sessionmaker(bind=engine)
session = session()

if not database_exists(engine.url):
    create_database(engine.url)

print(database_exists(engine.url))

from tkinter import *

root = Tk()

root.title('Invoices For Payment')
root.geometry('500x%s' % 600) # Size 200, 200

def button_callback():
    global button, listbox, open_invoices
    total = 0
    for s in listbox.curselection():
        total += open_invoices[s].camount()
    print('Total credit to apply %s' % total)

button = Button(root,
                text="Calculate credit to apply to check",
                name="calculate-credit-button",
                command = button_callback,
                padx=7, pady=2)
button.pack()

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

invoices = [c for c in session.query(Invoice).filter(Invoice.voided==False)]
listbox = Listbox(
    root,
    selectmode=EXTENDED,
    width=400, height=len(invoices),
    yscrollcommand=scrollbar.set
)
listbox.pack()

# fixme: remove amount field in Invoice model, change camount() to amount()
#   setup a 'helper/lib' to be an API to models.py
open_invoices = []
for i in invoices:
    if i.camount() > 0:
        open_invoices.append(i)
for i in open_invoices:
    listbox.insert(END, i)

scrollbar.config(command=listbox.yview)
root.mainloop()
