# encoding: utf-8

from __future__ import unicode_literals

from xmlrpclib import Fault

from web.auth import authenticated, user
from web.core import Controller, config

from sound.irc.atheme import Atheme
from sound.irc.util import StartupMixIn
from sound.irc.auth.controller import AuthenticationMixIn


log = __import__('logging').getLogger(__name__)


class RootController(Controller, StartupMixIn, AuthenticationMixIn):
    def index(self):
        if authenticated:
            return 'sound.irc.template.index', dict()

        return 'sound.irc.template.welcome', dict()

    def process_groups(self, atheme):
        for group in user.tags:
            atheme.command('GroupServ', 'FLAGS', '!%s' % group, user.transform_to_nick(), '+c')

    def process_cloak(self, atheme):
        try:
            atheme.command('NickServ', 'VHOST', user.transform_to_nick(), user.get_cloak())
        except Fault as f:
            if f.faultCode != 12: # fault_nochange
                raise

    def passwd(self, password):
        try:
            atheme = Atheme(config['irc.backend'], config['irc.username'], config['irc.password'],
                            config['irc.robotip'])
            try:
                irc_nick = user.transform_to_nick()
                try:
                    exists = atheme.command('NickServ', 'INFO', irc_nick)
                except Fault:
                    exists = False
                if not exists:
                    result = atheme.command('NickServ', 'FREGISTER',
                                            irc_nick, password, '%s@%s' % (irc_nick, config['irc.core_domain']))
                    self.process_groups(atheme)
                    self.process_cloak(atheme)
                else:
                    self.process_groups(atheme)
                    self.process_cloak(atheme)
                    return 'json:', dict(success=False, message="Already registered. Contact #help")
            finally:
                atheme.logout()
        except Exception as e:
            log.exception("Error attempting to assign password.")
            return 'json:', dict(success=False, message=str(e))

        return 'json:', dict(success=True, message=result)
