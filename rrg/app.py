#!/usr/local/bin/python
import os

from flask import Flask

app = Flask(__name__, instance_relative_config=True)
# fixme: delete this file, opting for app_engine
# Load the default configuration
SETTINGS_FILE = os.environ.get('RRG_SETTINGS', 'bad_file')

if os.path.isfile(SETTINGS_FILE):
    try:
        app.config.from_envvar('RRG_SETTINGS')
    except Exception as e:
        print('something went wrong with config file %s' % SETTINGS_FILE)
        quit(1)
else:
    print('Settings file %s does not exist.' % SETTINGS_FILE)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(app.config['RRG_PORT']))
