from sqlalchemy import create_engine


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
    if args.mysql_host == 'localhost':
        engine = create_engine(
            'mysql+mysqldb://%s:%s@%s:%s/%s' % (args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db))

        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    else:
        print('This routine only builds test databases on localhost')