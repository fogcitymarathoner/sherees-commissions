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
    global button, listbox, invoices

    selected_invoices = listbox.curselection()
    selected_invoices = [invoices[int(item)] for item in selected_invoices]
    print('item selection %s' % selected_invoices )
    print(listbox.curselection())
    print('hi button-name %s' % button['text'])
    for s in listbox.curselection():
        print(invoices[s])

button = Button(root, text="Calculate Credit", name="calculate-credit-button",
                command = button_callback,
                padx=7, pady=2)
button.pack()

scrollbar = Scrollbar(root)
scrollbar.pack(side=RIGHT, fill=Y)

invoices = [c for c in session.query(Invoice).filter(Invoice.voided==False)]
listbox = Listbox(
    root, selectmode=EXTENDED, width=400, height=len(invoices), yscrollcommand=scrollbar.set)
listbox.pack()
print(session.query(Iitem).filter(Iitem.invoice_id==2988).first())
print('%s invoices' % len(invoices))
for i in invoices:
    print(i.id)
    print(i.invoice_items)
    for j in i.invoice_items:
        print(j.amount)
        print(j.quantity)
    print(i.camount())
    if i.camount() > 0:
        listbox.insert(END, i)

scrollbar.config(command=listbox.yview)
root.mainloop()
