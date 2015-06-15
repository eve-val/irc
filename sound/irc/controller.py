# encoding: utf-8

from __future__ import unicode_literals

from xmlrpclib import Fault

from web.auth import authenticate, authenticated, user
from web.core import Controller, config

from sound.irc.atheme import Atheme
from sound.irc.util import StartupMixIn
from sound.irc.auth.controller import AuthenticationMixIn


log = __import__('logging').getLogger(__name__)


class RootController(Controller, StartupMixIn, AuthenticationMixIn):
    def index(self):
        if authenticated:
            atheme = self.get_atheme()
            exists = self.user_exists(atheme)
            return 'sound.irc.template.index', dict(exists=exists)

        return 'sound.irc.template.welcome', dict()

    def get_atheme(self):
        return Atheme(config['irc.backend'], config['irc.username'], config['irc.password'],
                      config['irc.robotip'])

    def user_exists(self, atheme):
        try:
            atheme.command('NickServ', 'INFO', user.transform_to_nick())
            return True
        except Fault:
            return False

    def process_groups(self, atheme):
        for group in user.tags:
            atheme.command('GroupServ', 'FLAGS', '!%s' % group, user.transform_to_nick(), '+c')

    def process_cloak(self, atheme):
        try:
            atheme.command('NickServ', 'VHOST', user.transform_to_nick(), user.get_cloak())
        except Fault as f:
            if f.faultCode != 12: # fault_nochange
                raise

    def update_access(self):
        try:
            authenticate(user.token)
            atheme = self.get_atheme()
            try:
                irc_nick = user.transform_to_nick()
                if not self.user_exists(atheme):
                    return 'json:', dict(success=False, message="Can only update access for an existing irc registration")
                self.process_groups(atheme)
                self.process_cloak(atheme)
            finally:
                atheme.logout()
        except Exception as e:
            log.exception("Error attempting to update access.")
            return 'json:', dict(success=False, message="Error updating access! {}" + str(e))

        return 'json:', dict(success=True, message="Updated with groups: " + ", ".join(user.tags))
    def passwd(self, password):
        try:
            authenticate(user.token)
            atheme = self.get_atheme()
            try:
                irc_nick = user.transform_to_nick()
                if self.user_exists(atheme):
                    atheme.command('NickServ', 'FDROP', irc_nick)
                result = atheme.command('NickServ', 'FREGISTER',
                                        irc_nick, password, '%s@%s' % (irc_nick, config['irc.core_domain']))
                self.process_groups(atheme)
                self.process_cloak(atheme)
            finally:
                atheme.logout()
        except Exception as e:
            log.exception("Error attempting to assign password.")
            return 'json:', dict(success=False, message=str(e))

        return 'json:', dict(success=True, message=result)
