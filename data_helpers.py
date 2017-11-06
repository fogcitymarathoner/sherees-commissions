"""Loose functions moved out of models.py"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqlalchemy import exc
from sqlalchemy import desc
from  rrg import models
engine = create_engine("postgres://marc:flaming@localhost:5432/biz")
session = sessionmaker(bind=engine)
session = session()

def count_vendors():
    """Get vendors total db count."""
    try:
        objs = session.query(models.Vendor).all()
    except exc.OperationalError:
        raise
    else:
        return len(objs)

def list_page_vendors_arrays(page=1, page_size=30):
    """Get list of vendor arrays."""
    offset = (page - 1) * page_size
    try:
        objs = session.query(models.Vendor).order_by(
            desc(models.Vendor.modified_date)). \
            limit(page_size). \
            offset(offset)
    except exc.OperationalError:
        raise
    else:
        return [c.to_array() for c in objs]