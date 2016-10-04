from os import urandom, path


# Web Server
CSRF_ENABLED = True
SECRET_KEY = urandom(30)
PROPAGATE_EXCEPTIONS = True
REMEMBER_COOKIE_NAME = 'tournament_token'   # Needs to be unique server-wide.

# SQLAlchemy
basedir = path.abspath(path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(path.join(basedir, 'app.db'))
SQLALCHEMY_TRACK_MODIFICATIONS = False

# LDAP
LDAP_URI = 'ldap://YOUR.LDAP.URI'
LDAP_SEARCH_BASE = 'ou=????,dc=????,dc=????'

ADMIN_USERS = ['LDAP.USER.ID.HERE']

# The number of people at an ideal drafting table.
IDEAL_TABLE = 8

