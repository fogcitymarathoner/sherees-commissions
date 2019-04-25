import os

SQLALCHEMY_DATABASE_URI = os.environ.get(
    'BUSINESS_DATABASE_URI',
    "sqlite:////biz.db"
)
SQLALCHEMY_TRACK_MODIFICATIONS = False

if os.environ.get('AWS_ACCESS_KEY_ID'):
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
else:
    print('Environment Variable AWS_ACCESS_KEY_ID not set')
    quit(1)

if os.environ.get('AWS_SECRET_ACCESS_KEY'):
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
else:
    print('Environment Variable AWS_SECRET_ACCESS_KEY not set')
    quit(1)
