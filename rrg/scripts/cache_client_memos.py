import os


from flask_script import Manager
from flask import Flask
from rrg.billing import cache_non_date_parsed as routine
from rrg.models import session_maker
from rrg.models import ClientMemo
from rrg.utils import clients_managers_dir

app = Flask(__name__, instance_relative_config=True)

# Load the default configuration
if os.environ.get('RRG_SETTINGS'):
    settings_file = os.environ.get('RRG_SETTINGS')
else:
    print('Environment Variable RRG_SETTINGS not set')
    quit(1)

if os.path.isfile(settings_file):
    try:
        app.config.from_envvar('RRG_SETTINGS')
    except Exception as e:
        print('something went wrong with config file %s' % settings_file)
        quit(1)
else:
    print('settings file %s does not exits' % settings_file)


def cache_client_memos_ep():
    """
    replaces cake cache clients memos
    """
    args = parser.parse_args()
    session = session_maker(args.db_user, args.db_pass, args.mysql_host, args.mysql_port, args.db)
    print('Caching Clients-Memos %s into %s' % (args.db, clients_managers_dir(args.datadir)))
    routine(session, clients_managers_dir(args.datadir), ClientMemo)
    session.commit()


manager = Manager(app)


@manager.command
def cache_client_memos():
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    print('Caching Clients-Memos %s into %s' % (app.config['DB'], clients_managers_dir(app.config['DATADIR'])))
    routine(session, clients_managers_dir(app.config['DATADIR']), ClientMemo)
    session.commit()

if __name__ == "__main__":
    manager.run()
