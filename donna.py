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
            
            http = sqlite_get_field(c, 'ip', 'http')
            http_weights = sqlite_get_field(c, 'status', 'http')
            
            https = sqlite_get_field(c, 'ip', 'https')
            https_weights = sqlite_get_field(c, 'status', 'https')
            
            proxy = {
            'http': 'http://' + random.choices(http,
                                               weights=http_weights)[0],
            'https': 'https://' + random.choices(https,
                                                 weights=https_weights)[0]
                     }

        self.proxy = proxy
        self.count = 0
        self.start = time.time()
        self.blocked = 0
        self._session = requests.Session()
        self._session.proxies = dict(self.proxy)
        self._session.max_redirects = 10
        # print(proxy)
        return proxy

    def finalize_proxy(self, ver=False):
        proxyManager._session = None
        if not self.proxy:
            self.count = 0
            return 'no proxy to finalize'
        with sqlite3.connect(self.proxyfile) as p:
            c = p.cursor()
            c.execute('PRAGMA journal_mode = MEMORY')
            status_update(c, self, 'http')
            status_update(c, self, 'https')

        self.proxy = dict()
        self.count = 0

def get_page(url, proxyManager, timeout=5, https=True):
    if not proxyManager.proxy:
        proxyManager.get_proxy()
    page = None

    while page == None:
        if not https:
            del proxyManager._session.proxies['https']
        while page == None:
            try:
                page = proxyManager._session.get(url, timeout=timeout)
            except (requests.exceptions.ConnectionError, 
                    requests.exceptions.Timeout) as e:
                proxyManager.finalize_proxy()
                proxyManager.get_proxy()
                
        if 'verification page' in page.content[:200].decode('utf-8'):
            print(' ', end='', flush=True)
            proxyManager.blocked = 1
            proxyManager.finalize_proxy()
            proxyManager.get_proxy()
            page = None
            
    proxyManager.count = proxyManager.count + 1
    return page


def sqlite_get_field(cursor, field, table):
    cursor.execute('SELECT {} FROM {}'.format(field, table))
    q = cursor.fetchall()
    q = [a[0] for a in q]
    return q


def status_update(cursor, proxyManager, protocol):
    ip = proxyManager.proxy[protocol].split('//')[1]
    total_time = time.time() - proxyManager.start
    count = proxyManager.count
    
    command = 'SELECT status FROM {} WHERE ip = ?'.format(protocol)
    cursor.execute(command, [ip])
    
    status = cursor.fetchone()[0]
    status = pow(status, 0.9) + pow(count, 0.9) * 10

    command = 'UPDATE {} SET status = ? WHERE ip = ?'.format(protocol)
    cursor.execute(command, [status, ip])
    
    command = 'UPDATE {} SET blocked = ? WHERE ip = ?'.format(protocol)
    cursor.execute(command, [proxyManager.blocked, ip])
