# -*- coding: utf-8 -*-
# Copyright (c) 20015 by Valeriy Solovyov <weldpua2008@gmail.com>
# All Rights Reserved.
# Licensed to MIT License:
#  Permission is hereby granted, free of charge,
# to any person obtaining a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import cherrypy
import random
import logging
import argparse
import os

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.websocket import WebSocket
from ws4py.messaging import TextMessage
from jinja2 import Environment, FileSystemLoader
from ws4py import configure_logger


SUBSCRIBERS = set()
env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

__author__ = "Valeriy Solovyov (weldpua2008@gmail.com)"
__copyright__ = "Copyright (C) 2015 Valeriy Solovyov"
__license__ = "MIT"
__version__ = "1.0"



class WebSocketHandler(WebSocket):
    sessionId = 'websocket-broadcast'
    def __init__(self, *args, **kw):
        WebSocket.__init__(self, *args, **kw)

        # cherrypy.log("args type %s" % type(ws))
        #
        # for i in args:
        #     try:
        #         cherrypy.log("args  %s \n" % i)
        #     except Exception as error:
        #         cherrypy.log("Can't print args  because %s \n" % error)
        # cherrypy.log("args %s " % args)
        # cherrypy.log("kw %s " % kw)
        SUBSCRIBERS.add(self)

    def received_message(self, msg):
        # cherrypy.log("args environ %s " % self.environ['QUERY_STRING'])
        cherrypy.log('sessionId %s received_message %s' % (self.sessionId, msg))
        cherrypy.engine.publish(str(self.sessionId), msg)
        try:
            cherrypy.log('SUBSCRIBERS %s' % SUBSCRIBERS)
        except Exception:
            pass

    def closed(self, code, reason="A client left the room without a proper explanation."):
        cherrypy.engine.publish(str(self.sessionId), TextMessage(reason))
        SUBSCRIBERS.remove(self)


class Root(object):
    def __init__(self, host, port, ssl=False):
        self.host = host
        self.port = port
        self.scheme = 'wss' if ssl else 'ws'

    @cherrypy.expose
    def index(self):
        tmpl = env.get_template('index.html')
        return tmpl.render(
            username="User%d" % random.randint(0, 100),
            host=self.host,
            port=self.port,
            scheme=self.scheme)

    @cherrypy.expose
    def ws(self, sessionId):
        cherrypy.log("Handler created: %s" % repr(cherrypy.request.ws_handler))
        cherrypy.log("sessionId: %s" % sessionId)
        # cherrypy.request.ws_handler.sessionId = sessionId

    @cherrypy.expose
    def notify(self, msg):
        for conn in SUBSCRIBERS:
            conn.send(msg)

if __name__ == '__main__':

    configure_logger(level=logging.DEBUG)

    parser = argparse.ArgumentParser(description='Echo CherryPy Server')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('-p', '--port', default=9000, type=int)
    parser.add_argument('--ssl', action='store_true')
    args = parser.parse_args()

    cherrypy.config.update({'server.socket_host': args.host,
                            'server.socket_port': args.port,
                            'tools.staticdir.root': os.path.abspath(os.path.join(os.path.dirname(__file__), 'static'))})

    if args.ssl:
        CRT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'keys/server.crt'))
        KEY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'keys/server.key'))
        cherrypy.config.update({'server.ssl_certificate': CRT_PATH,
                                'server.ssl_private_key': KEY_PATH})

    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.quickstart(Root(args.host, args.port, args.ssl), '', config={
        '/ws': {
            'tools.websocket.on': True,
            'tools.websocket.handler_cls': WebSocketHandler
            },
        '/js': {
              'tools.staticdir.on': True,
              'tools.staticdir.dir': 'js'
            }
        }
    )