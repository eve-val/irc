# encoding: utf-8

from __future__ import unicode_literals

import xmlrpclib
from xmlrpclib import Fault

from web.auth import authenticated, user
from web.core import Controller, config

from sound.irc.util import StartupMixIn
from sound.irc.auth.controller import AuthenticationMixIn


log = __import__('logging').getLogger(__name__)


class RootController(Controller, StartupMixIn, AuthenticationMixIn):
    def index(self):
        if authenticated:
            return 'sound.irc.template.index', dict()

        return 'sound.irc.template.welcome', dict()

    def process_groups(self, c, token):
        robot_ip = config['irc.robotip']
        robot_username = config['irc.username']
        for group in user.tags:
            c.atheme.command(token, robot_username, robot_ip, 'GroupServ', 'FLAGS', '!%s' % group, user.transform_to_nick(), '+c')

    def process_cloak(self, c, token):
        robot_ip = config['irc.robotip']
        robot_username = config['irc.username']
        c.atheme.command(token, robot_username, robot_ip, 'NickServ', 'VHOST',
                         user.transform_to_nick(), user.get_cloak())

    def passwd(self, password):
        try:
            robot_ip = config['irc.robotip']
            robot_username = config['irc.username']
            c = xmlrpclib.ServerProxy(config['irc.backend'])
            token = c.atheme.login(robot_username, config['irc.password'], robot_ip)
            if not token:
                raise Exception('Could not get auth token.')
            try:
                irc_nick = user.transform_to_nick()
                try:
                    exists = c.atheme.command(token, robot_username, robot_ip, 'NickServ', 'INFO',
                                              irc_nick)
                except Fault:
                    exists = False
                if not exists:
                    result = c.atheme.command(token, robot_username, robot_ip, 'NickServ', 'FREGISTER',
                                              irc_nick, password, '%s@%s' % (irc_nick, config['irc.core_domain']))
                    self.process_groups(c, token)
                    self.process_cloak(c, token)
                else:
                    self.process_groups(c, token)
                    self.process_cloak(c, token)
                    return 'json:', dict(success=False, message="Already registered. Contact #help")
            finally:
                c.atheme.logout(token, robot_username)
        except Exception as e:
            log.exception("Error attempting to assign password.")
            return 'json:', dict(success=False, message=str(e))

        return 'json:', dict(success=True, message=result)
