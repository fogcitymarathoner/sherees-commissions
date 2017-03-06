import os
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from sqlalchemy.orm import sessionmaker
import xml.etree.ElementTree as ET

from rrg.models import Base
from rrg.models import Client
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

sdir = os.path.join('datadir', 'biz', 'states')

for dirName, subdirList, filelist in os.walk(sdir, topdown=False):
    for f in filelist:
        state = State()
        doc = ET.parse(os.path.join('datadir', 'biz', 'states', f))
        state.name = doc.findall('name')[0].text
        state.post_ab = doc.findall('post_ab')[0].text
        state.capital = doc.findall('capital')[0].text
        state.date = doc.findall('date')[0].text
        state.flower = doc.findall('flower')[0].text
        session.add(state)

for c in session.query(State):
    print(c)

clientsx = ['00062.xml', '00116.xml', '00185.xml']
session.add(User(firstname='Marc', lastname='Condon'))
for c in clientsx:
    f = os.path.join('datadir', 'biz', 'clients', c)
    print(f)

    if os.path.isfile(f):
        doc = ET.parse(f)

    print(doc.findall('name')[0].text)
    client = Client()
    client.id = int(doc.findall('id')[0].text)
    client.name = doc.findall('name')[0].text
    client.street1 = doc.findall('street1')[0].text
    client.street2 = doc.findall('street2')[0].text
    client.city = doc.findall('city')[0].text
    client.state_id = int(doc.findall('state_id')[0].text)
    client.zip = doc.findall('zip')[0].text
    client.terms = int(doc.findall('terms')[0].text)
    session.add(client)
for c in session.query(Client):
    print(c)

session.commit()
