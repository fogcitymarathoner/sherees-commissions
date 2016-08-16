
from rrg import engine
from rrg.models import Contract
from rrg.models import Base


def clear_out_bad_contracts():
    """
    removed contracts from the database that have either employee_id or
    client_id 0 or None
    """
    session.query(
        Contract).filter(
        Contract.employee_id == 0, Contract.client_id == 0).delete(
        synchronize_session=False)
    session.commit()


def create_db():
    """
    this routine has a bug, DATABASE isn't fully integrated right, the line
    DATABASE = 'rrg' in rrg/__init__.py has to be temporarily hardcoded to
    'rrg_test' or whatever
    :return:
    """
    Base.metadata.create_all(engine)
