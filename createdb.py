from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from rrg.models import Base

engine = create_engine("postgres://postgres:mysecretpassword@192.168.99.100:32770/biz")
if not database_exists(engine.url):
    create_database(engine.url)

print(database_exists(engine.url))

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)