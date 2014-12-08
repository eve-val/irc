import xmlrpclib

class Atheme(object):
    def __init__(self, backend, username, password, ip):
        self.conn = xmlrpclib.ServerProxy(backend)
        self.username = username
        self.ip = ip
        self.token = self.conn.atheme.login(username, password, ip)
        if not self.token:
            raise Exception('Could not get auth token.')

    def command(self, service, command, *args):
        return self.conn.atheme.command(self.token, self.username, self.ip,
                                        service, command, *args)

    def logout(self):
        self.conn.atheme.logout(self.token, self.username)
