#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import Queue
import sys
import time
import logging
import requests
import simplejson as json
import argparse
from pyb import __version__

statsQ = Queue.Queue()


class MyThread(threading.Thread):
        def __init__(self, func):
            threading.Thread.__init__(self)
            self.func = func
            self.queue = Queue.Queue()
            self.total_req = 0
            self.total_time_list = []
            self.length_list = []
            self.header = {
                'server': ''
            }

        def kill(self):
            self.queue.put(None)

        def run(self):
            while True:
                try:
                    j = self.queue.get()
                    if j is None:
                        self.statistics()
                        break
                    self.func(j, self.header, self.total_time_list, self.length_list)
                except Queue.Empty:
                    continue

        def add_job(self, job):
            self.total_req += 1
            self.queue.put(job)

        def statistics(self):
            global statsQ
            succeed = len(self.total_time_list)
            failed = self.total_req - succeed
            total_time = reduce(lambda x, y: x+y, self.total_time_list)
            total_length = reduce(lambda x, y: x+y, self.length_list)
            info = {
                'total_req': self.total_req,
                'succeed_req': succeed,
                'failed_req': failed,
                'total_time': total_time,
                'total_length': total_length,
            }
            statsQ.put(json.dumps(info))


class Controller():
    def __init__(self, t_max=300):
        self.max_thread = t_max
        self.die = False
        self.TL = []
        self.thread_index = 0

    def put_job(self, job):
        thr = self.TL[self.thread_index]
        thr.add_job(job)
        self.thread_index = (self.thread_index + 1) % self.max_thread

    def start(self, func):
        for i in range(self.max_thread):
            s = MyThread(func)
            s.setDaemon(True)
            self.TL.append(s)
            s.start()

    def stop(self):
        for i in self.TL:
            i.kill()
        for i in self.TL:
            i.join()


def req(param, header, total_time_list, length_list):
    try:
        url, method, data = param
        start = time.time()
        if method == 'GET':
            r = requests.get(url)
        elif method == 'POST':
            data = data_parse(data)
            r = requests.post(url, data)
        elif method == 'DELETE':
            r = requests.delete(url)
        elif method == 'PUT':
            data = data_parse(data)
            r = requests.put(url, data)
        elif method == 'HEAD':
            r = requests.head(url)
        elif method == 'OPTIONS':
            r = requests.options(url)

        #print r.content
        total_time = time.time() - start
        if r.ok:
            if not header['server']:
                header['server'] = r.headers['Server'] if 'Server' in r.headers else 'unknown'
            if 'Content-Length' in r.headers:
                length = float(r.headers['Content-Length'])
            else:
                length = len(r.content)
            total_time_list.append(total_time)
            length_list.append(length)
    except Exception, e:
        logging.warn('request failed, domain:%s ; :%s' % (url, e), exc_info=1)

def data_parse(data):
    params = data.split('&')
    data_json = dict()
    for param in params:
        if param:
            p = param.split('=')
            if p and len(p) == 2:
                data_json[p[0]] = p[1]
    return data_json

def bench(args):
    c = args['concurrency']
    n = args['requests']
    param = (args['url'], args['method'], args['data'])
    if n < c:
        print 'total num must gt concurrent num'
        sys.exit(0)
    ctrl = Controller(c)
    ctrl.start(req)
    for x in xrange(n):
        ctrl.put_job(param)
    ctrl.stop()
    stats = dict()
    for i in xrange(c):
        stat = statsQ.get()
        stat = json.loads(stat)
        for k, v in stat.items():
            if k not in stats:
                stats[k] = v
            else:
                stats[k] += v

    total_length = stats['total_length']
    total_time = stats['total_time']
    succeed_req = stats['succeed_req']
    avg_time = total_time / succeed_req
    stats['total_time'] = '%.2f' % total_time
    stats['avg_length'] = '%.2f' % (total_length / succeed_req)
    stats['avg_time'] = '%.2f' % avg_time
    stats['rps'] = '%.2f' % (1 / avg_time)
    stats['rate'] = '%.2f' % (total_length / total_time / 1024)
    return stats


def arg_parse():
    parser = argparse.ArgumentParser()
    methods = ('GET', 'POST', 'DELETE', 'PUT', 'HEAD', 'OPTIONS')
    parser.add_argument('-v', '--version', action='store_true', default=False, help='Displays version and exits.')
    parser.add_argument('-n', '--requests', help='Number of requests', type=int, default=1)
    parser.add_argument('-c', '--concurrency', help='Concurrency', type=int, default=1)
    parser.add_argument('-m', '--method', help='HTTP Method', type=str, default='GET', choices=methods)
    parser.add_argument('-d', '--data', help='Request Data, for example: "id=1&name=lu"', type=str)
    parser.add_argument('url', help='URL to hit', nargs='?')

    args = parser.parse_args()
    if args.version:
        print(__version__)
        sys.exit(0)

    if args.url is None:
        print('You need to provide an URL.')
        parser.print_usage()
        sys.exit(0)

    if args.method not in methods:
        print('You provide an HTTP Method invalid.')
        parser.print_usage()
        sys.exit(0)

    if args.data is not None and args.method not in ('POST', 'PUT'):
        print("You can't provide data with %r" % args.method)
        parser.print_usage()
        sys.exit(0)

    args = dict((name, getattr(args, name)) for name in dir(args) if not (name.startswith('__') or name.startswith('_')))
    return args


def main():
    print bench(arg_parse())

if __name__ == "__main__":
    main()

