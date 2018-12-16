# -*- coding: utf-8 -*-

import json
import logging
import os

from tornado import httpserver, ioloop, options, web
from tornado.log import enable_pretty_logging

from module import *

enable_pretty_logging()


def update(text):
    global topo, db
    topo = update_topo(text)
    db = build_graph_dict(**topo)


class IndexHandler(web.RequestHandler):

    def get(self):
        self.redirect('/index.html')


class ApiHandler(web.RequestHandler):

    def get(self, action, *args):
        if action == 'link':
            with open('link.txt') as f:
                link = f.read()
            self.write(dict(link=link, topo=topo, location=loc))
        elif action == 'topo':
            self.write(topo)

    def post(self, action, *args):
        d = json.loads(self.request.body)
        if action == 'link':
            text = d['link'].strip()
            with open('link.txt', 'w') as f:
                f.write(text)
            update(text)
            self.write(dict(topo=topo))
        elif action == 'path':
            self.write(dict(path=get_path(db, d['src'], d['dst'])))


if __name__ == '__main__':
    options.define('p', default=9898, help='run on the given port', type=int)
    options.parse_command_line()
    port = options.options.p

    root_path = os.path.dirname(__file__)

    with open('link.txt') as f:
        update(f.read())
    global loc
    with open('location.json') as f:
        loc = json.load(f)

    settings = dict(
        static_path=os.path.join(root_path, 'static'),
        cookie_secret='61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=',
        autoreload=True,
    )
    handlers = [
        (r'/', IndexHandler),
        (r'/static/(.*)', web.StaticFileHandler),
        (r'/api/data/(.*)', ApiHandler),
        (r'/(.*\.html)', web.StaticFileHandler, {'path': root_path}),
    ]

    web_app = web.Application(handlers, **settings)
    server = httpserver.HTTPServer(web_app, max_buffer_size=1048576000)
    server.bind(port)

    print('Web server started on port %d' % port)
    print('Press "Ctrl+C" to exit.\n')

    server.start()

    try:
        ioloop.IOLoop.instance().current().start()
    except KeyboardInterrupt:
        print(' received, exited.\n')
