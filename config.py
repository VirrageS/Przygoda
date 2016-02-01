import os

base_dir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = b'R\x9by\xc0\xaa\xee\xf6\xcd\x18\xa7\xd3\xc5\x1dU\xb4\xde\x00\xe67\xc3/\xe7\xaa\x06V\x92\xbb\xa1\x93]\xcd\xc0\xfd\xd2U\x98\x84h\xb7\xf3\xec\x94\x14\x8bk\x8a\xc2\x17\x16\xf5'
    API_KEY = str(os.environ.get('API_KEY'))

    # database
    DATABASE_QUERY_TIMEOUT = 1
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'app.db')

    # facebook auth
    OAUTH_CREDENTIALS = {
        'facebook': {
            'id': str(os.environ.get('CREDENTIALS_FB_ID')),
            'secret': str(os.environ.get('CREDENTIALS_FB_SECRET'))
        },
        'twitter': {
            'id': '3RzWQclolxWZIMq5LJqzRZPTl',
            'secret': 'm9TEd58DSEtRrZHpz2EjrV9AhsBRxKMo8m3kuIZj3zLwzwIimt'
        }
    }

    # csrf
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = "somethingimpossibletoguess"
    WTF_CSRF_ENABLED = True

    # token password salt
    SECURITY_PASSWORD_SALT = b'R\x9by\xc0\xaa\xee\xf6\xcd\x18\xa7\xd3\xc5\x1dU\xb4\xde\x00\xe67\xc3/\xe7\xaa\x06V\x92\xbb\xa1\x93]\xcd\xc0\xfd\xd2U\x98\x84h\xb7\xf3\xec\x94\x14\x8bk\x8a'

    # email server
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    # gmail authentication
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

    # mail accounts
    MAIL_DEFAULT_SENDER = 'from@sportoweprzygody.pl'

    # how many days from today statistics coverage
    STATISTICS_DAYS_SPAN = 20

    # babel settings
    BABEL_DEFAULT_LOCALE = 'pl'

    # database config
    DATABASE_USERNAME = str(os.environ.get('DATABASE_USERNAME'))
    DATABASE_PASSWORD = str(os.environ.get('DATABASE_PASSWORD'))

    # celery settings
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = ('postgresql://' + str(os.environ.get('DATABASE_USERNAME')) +
                              ':' + str(os.environ.get('DATABASE_PASSWORD')) +
                              '@' + str(os.environ.get('DATABASE_HOST')) +
                              ':' + str(os.environ.get('DATABASE_PORT')) +
                              '/' + str(os.environ.get('DATABASE_NAME')) + '')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'app.db')

class TestingConfig(Config):
    BABEL_DEFAULT_LOCALE = 'en'
    TESTING = True
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'test.db')
