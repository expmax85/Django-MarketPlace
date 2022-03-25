from django.contrib.sessions.backends.db import SessionStore as DbSessionStore


class SessionStore(DbSessionStore):
    """ Не сбрасывать сессию """

    def cycle_key(self):
        pass
