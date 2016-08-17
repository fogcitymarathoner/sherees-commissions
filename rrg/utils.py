from sqlalchemy import create_engine
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


class Args(object):
    mysql_host = 'localhost'
    mysql_port = 3306
    db_user = 'root'
    db_pass = 'my_very_secret_password'
    db = 'rrg_test'


def create_db():
    """
    this routine has a bug, DATABASE isn't fully integrated right, the line
    DATABASE = 'rrg' in rrg/__init__.py has to be temporarily hardcoded to
    'rrg_test' or whatever
    :return:
    """
    args = Args()

    engine = create_engine(
        'mysql+mysqldb://%s:%s@%s:%s/%s' % (
            args.db_user, args.db_pass, args.mysql_host,
            args.mysql_port, args.db))

    Base.metadata.create_dropall(engine)
    Base.metadata.create_all(engine)
