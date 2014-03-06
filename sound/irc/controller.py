# encoding: utf-8

from __future__ import unicode_literals

import xmlrpclib

from web.auth import authenticated, user
from web.core import Controller

from sound.irc.util import StartupMixIn
from sound.irc.auth.controller import AuthenticationMixIn


log = __import__('logging').getLogger(__name__)

SERVER_HOST = 'http://127.0.0.1:30816/xmlrpc'
USERNAME = 'webapp'
IP_ADDRESS = '127.0.0.1'
PASSWORD = 'QkUJddpyVzGDZXKQmW0MVpbZ03nrjj5w'

class RootController(Controller, StartupMixIn, AuthenticationMixIn):
    def index(self):
        if authenticated:
            return 'sound.irc.template.index', dict()

        return 'sound.irc.template.welcome', dict()
    
    def passwd(self, password):
        u = user._current_obj()
        
        try:
          c = xmlrpclib.ServerProxy(SERVER_HOST)
          token = c.atheme.login(USERNAME, PASSWORD, IP_ADDRESS)
          if not token:
            raise Exception('Could not get auth token.')
          try:
            result = c.atheme.command(token, USERNAME, IP_ADDRESS, 'NickServ', 'FREGISTER',
                                      'june_ting', password, 'june_ting@auth.of-sound-mind.com')
          finally:
            c.atheme.logout(token, USERNAME)
        except:
            log.exception("Error attempting to assign password.")
            return 'json:', dict(success=False, message="Something terrible happened.")
        
        return 'json:', dict(success=True, message=result)
