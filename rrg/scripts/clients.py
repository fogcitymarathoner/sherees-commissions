import os

from flask_script import Manager
from flask import Flask
from tabulate import tabulate

from rrg.models import session_maker
from rrg.models import Client
from rrg.models_api import generate_ar_report, session_maker
from rrg.clients import selection_list_all
from rrg.clients import selection_list_active
from rrg.clients import selection_list_inactive


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


manager = Manager(app)


@manager.command
def all():
    """
    show list of all clients in database
    :return:
    """
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    print(
        tabulate(
            selection_list_all(session),
            headers=['number', 'sqlid', 'name', 'city', 'state']))


@manager.command
def active():
    """
    show list of active clients in database
    :return:
    """
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])


    print(
        tabulate(
            selection_list_active(session),
            headers=['number', 'sqlid', 'name', 'city', 'state']))


@manager.command
def ar():
    """
    rolling workflow for an active client's ar
    :return:
    """

    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])
    client_list = selection_list_active(session)
    print(
        tabulate(
            client_list,
            headers=['number', 'sqlid', 'name', 'city', 'state']))

    selection = input("Please select an employee or 'q' to quit: ")
    if selection == 'q':
        quit()
    selected_client = client_list[int(selection)-1]

    client = session.query(Client).get(int(selected_client[1]))
    print('%s' % client.name)

    selection = input("Please select an ar report type [all, cleared, pastdue, open] or 'q' to quit: ")
    if selection == 'q':
        quit()
    if selection not in ['all', 'cleared', 'pastdue', 'open']:
        print('Wrong Ar type selected')
        quit()

    print(generate_ar_report(app, selection))

@manager.command
def inactive():
    """
    show list of inactive clients in database
    :return:
    """
    session = session_maker(
        app.config['MYSQL_USER'], app.config['MYSQL_PASS'], app.config['MYSQL_SERVER_PORT_3306_TCP_ADDR'],
        app.config['MYSQL_SERVER_PORT_3306_TCP_PORT'], app.config['DB'])

    print(
        tabulate(
            selection_list_inactive(session),
            headers=['number', 'sqlid', 'name', 'city', 'state']))


if __name__ == "__main__":
    manager.run()
