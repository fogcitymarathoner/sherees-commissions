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

clientsx = ['00062.xml', '00116.xml', '00185.xml']
session.add(User(firstname='Marc', lastname='Condon'))
for c in clientsx:
    f = os.path.join('datadir', 'biz', 'clients', c)
    print(f)

    if os.path.isfile(f):
        doc = ET.parse(f)

    print(doc.findall('name')[0].text)
    client = Client()
    client.name = doc.findall('name')[0].text
    client.terms = int(doc.findall('terms')[0].text)
    session.add(client)
for c in session.query(Client):
    print(c)

session.commit()
