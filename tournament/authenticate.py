import ldap

from tournament import app
from models import User


def authenticate(username, password):
    user = None

    connection = ldap.initialize(app.config["LDAP_URI"])

    try:
        connection.protocol_version = ldap.VERSION3
        result = connection.search_s(app.config["LDAP_SEARCH_BASE"],
                                     ldap.SCOPE_SUBTREE,
                                     'uid={}'.format(username))

        if result:
            ((distinguished_name, entry),) = result     # Username is unique.
            connection.simple_bind_s(distinguished_name,
                                     password.encode('iso8859-1'))

            email = entry['mail'][0]
            name = entry['cn'][0]
            id = entry['uid'][0]

            user = User(name=name, id=id, email=email)

    finally:
        connection.unbind_s()
        return user

