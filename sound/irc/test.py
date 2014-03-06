import xmlrpclib

SERVER_HOST = 'http://127.0.0.1:30816/xmlrpc'
USERNAME = 'webapp'
IP_ADDRESS = '127.0.0.1'
PASSWORD = 'QkUJddpyVzGDZXKQmW0MVpbZ03nrjj5w'

c = xmlrpclib.ServerProxy(SERVER_HOST)

token = c.atheme.login(USERNAME, PASSWORD, IP_ADDRESS)

if not token:
  raise Exception('Could not get auth token.')

try:
  print c.atheme.command(token, USERNAME, IP_ADDRESS, 'NickServ', 'FREGISTER', 'june_ting', 'abcdef', 'june_ting@auth.of-sound-mind.com')
finally:
  c.atheme.logout(token, USERNAME)
