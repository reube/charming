#!/usr/bin/python

__author__ = 'andrew'

import tornado.web
import tornado.websocket
import tornado.httpserver
import tornado.ioloop


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print "open!"+str(self.request)

    def on_message(self, message):
        print "Your message was: " + message

    def on_close(self):
        pass


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/server/', WebSocketHandler)
        ]

        settings = {
            'template_path': 'templates'
        }
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    ws_app = Application()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(8090)
    tornado.ioloop.IOLoop.instance().start()