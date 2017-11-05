
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import data_helpers
import models

VALUE_INPUT_OPTION = 'RAW'


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def update_last_vendor_batch(service, spreadsheetId):
    """"""

    offset = int(data_helpers.count_vendors() / 30)
    values = data_helpers.list_page_contacts_arrays(offset=offset, page_size=30)

    rangeName = 'VENDORS!A%s:X%s' % (offset*30 + 2, (offset+1)*30 + 2)
    body = {
      'values': values,
        "majorDimension": "ROWS",
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheetId, range=rangeName,
        valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
    print('update result %s' % result)

def update_vendors(service, spreadsheetId):
    """"""

    for rng in range(0, int(data_helpers.count_vendors()/30)):
        rangeName = 'VENDORS!A%s:X%s' % (rng*30 + 2, (rng+1)*30 + 2)
        service.spreadsheets().values().clear(
            spreadsheetId=spreadsheetId, range=rangeName, body={}).execute()
        values = data_helpers.list_page_vendors_arrays(offset=rng, page_size=30)
        body = {
          'values': values,
          "majorDimension": "ROWS",
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheetId, range=rangeName,
            valueInputOption=VALUE_INPUT_OPTION, body=body).execute()
        print('update result %s' % result)
        print(rng)
    update_last_vendor_batch(service, spreadsheetId)


def update_vendors_sheet():
    """Dumps the vendors table into contacts sheet at google
    """

    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)

    spreadsheetId = '17ti0hGxmD-68XSX_EiS7zKBkg4K_GjHzGvixEuF8O6I/edit#gid=0'
    update_vendors(service, spreadsheetId)
