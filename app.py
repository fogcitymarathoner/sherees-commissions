"""This is only used with the manage.py"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config.from_object('config')
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
sessionMaker = sessionmaker(bind=engine)
session = sessionMaker()
db = SQLAlchemy(app)

if __name__ == '__main__':
    app.run()