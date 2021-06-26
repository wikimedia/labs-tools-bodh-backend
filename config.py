import os
basedir = os.path.abspath(os.path.dirname(__file__))


class config(object):
    DEBUG = False
    TESTING = False


class production(config):
    DEBUG = False
    CONSUMER_KEY = ""
    CONSUMER_SECRET = ""
    OAUTH_MWURI = "https://www.wikidata.org/w/"
    SESSION_COOKIE_SECURE = True
    SESSION_REFRESH_EACH_REQUEST = False
    PREFERRED_URL_SCHEME = 'https'
    APP_REDIRECT_URI = "https://bodh.toolforge.org/"


class local(config):
    DEVELOPMENT = True
    DEBUG = True
    CONSUMER_KEY = ""
    CONSUMER_SECRET = ""
    OAUTH_MWURI = "https://test.wikidata.org/w/"
    APP_REDIRECT_URI = "http://localhost:3000/"
