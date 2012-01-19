from txtalert.env.settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'txtalert_dev',
    }
}

client = Client(
        servers=['http://localhost:4567/api/store/'], 
        key='my69eAMYjzqtmfaRJ107MeXCYDTaxQdNZPr8YOe/zOV5pIUoZa5biA=='
    )
setup_logging(SentryHandler(client))
