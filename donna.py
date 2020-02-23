#!/usr/bin/python


import sqlite3
import random
import requests
import time


class proxyManager:
    '''Manage your proxies'''
    def __init__(self, proxyfile):
        self.proxyfile = proxyfile
        self.count = 0
        self.proxy = dict()
        self._session = None

    def get_proxy(self):
        with sqlite3.connect(self.proxyfile) as p:
            c = p.cursor()
            c.execute('PRAGMA journal_mode = MEMORY')

            self.proxy = dict((
                (protocol,
                 protocol + '://' + random.choices(
                     _sqlite_get_field(c, 'ip', protocol),
                     weights=_sqlite_get_field(c, 'status', protocol)
                 )[0]) for protocol in ['http', 'https'])
            )

        self.count = 0
        self.start = time.time()
        return self.proxy

    def finalize(self, success_count=0):
        if not self.proxy:
            self.count = 0
            return 'no proxy to finalize'
        with sqlite3.connect(self.proxyfile) as p:
            c = p.cursor()
            c.execute('PRAGMA journal_mode = MEMORY')
            self._status_update(c, 'http')
            self._status_update(c, 'https')
        self.proxy = dict()
        self.count = 0

    def _status_update(self, cursor, protocol):
        ip = self.proxy[protocol].split('//')[1]
#         total_time = time.time() - proxyManager.start  
        count = self.count()
       
        command = 'SELECT status FROM {} WHERE ip = ?'.format(protocol)
        cursor.execute(command, [ip])
    
        status = cursor.fetchone()[0]
        status = pow(status, 0.9) + pow(count, 0.9) * 10
        command = 'UPDATE {} SET status = ? WHERE ip = ?'.format(protocol)
        cursor.execute(command, [status, ip])

def _sqlite_get_field(cursor, field, table):
    cursor.execute('SELECT {} FROM {}'.format(field, table))
    q = cursor.fetchall()
    q = [a[0] for a in q]
    return q

