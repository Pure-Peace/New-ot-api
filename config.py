import multiprocessing as mp
import os
from logger import log


# welcome
log('\n\nSTARTING OTSU API SERVICE...\n', 'r')


# config
log_dir = 'log'
current_path = os.getcwd()
if not os.path.exists(log_dir):
    os.makedirs(log_dir)


bind = '0.0.0.0:9529'
workers = mp.cpu_count() * 2
threads = 4
worker_class = 'gevent'
daemon = True


loglevel = 'info'
pidfile = f'{current_path}/{log_dir}/gunicorn.pid'
errorlog = f'{current_path}/{log_dir}/debug.log'
accesslog = f'{current_path}/{log_dir}/access.log'
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s'
'''
access_log_format:

h     remote address
l     '-'
u     currently '-', may be user name in future releases
t     date of the request
r     status line (e.g. ``GET / HTTP/1.1``)
s     status
b     response length or '-'
f     referer
a     user agent
T     request time in seconds
D     request time in microseconds
L     request time in decimal seconds
p     process ID
'''

# show config info
log('----WITH CONFIG----\n', 'b')
for i in [l for l in locals().items() if '__' not in l[0] and l[0] not in ('mp', 'os', 'log')]:
    log(f'{i[0]}: {i[1]}', 'g')
log('\nSERVICE STARTED!', 'y')