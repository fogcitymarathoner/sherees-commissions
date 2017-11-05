#!/usr/local/bin/python
"""
"""
import os

from flask import Flask
from flask import render_template

app = Flask(__name__, instance_relative_config=True)
# fixme: delete this file, opting for app_engine
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

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    home page
    """
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(app.config['RRG_PORT']))
