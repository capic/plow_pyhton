#!/usr/bin/env python

__author__ = 'Vincent'

import sys
import getopt
import logging
from treatment import Treatment

# from twisted.python import log
# from twisted.internet import reactor
# from autobahn.twisted.websocket import WebSocketServerProtocol
# from autobahn.twisted.websocket import WebSocketServerFactory
# from autobahn.twisted.websocket import WebSocketClientProtocol, \
# WebSocketClientFactory

# class NotificationServer(WebSocketServerProtocol):
# def onConnect(self, request):
# logging.debug("Client connecting: {}".format(request.peer))
# print("Client connecting: {}".format(request.peer))
#
# def onOpen(self):
# print("WebSocket connection open.")
#
# def onMessage(self, payload, isBinary):
# if isBinary:
# logging.debug("Binary message received: {} bytes".format(len(payload)))
# print("Binary message received: {} bytes".format(len(payload)))
# else:
# logging.debug("Text message received: {}".format(payload.decode('utf8')))
# print("Text message received: {}".format(payload.decode('utf8')))
#
# ## echo back message verbatim
# self.sendMessage(payload, isBinary)
#
# def onClose(self, wasClean, code, reason):
# print("WebSocket connection closed: {}".format(reason))


# class NotificationClient(WebSocketClientProtocol):
# def onConnect(self, response):
# print("Connected to Server: {}".format(response.peer))
# self.sendMessage(u"Hello, world!".encode('utf8'))
#
# def onMessage(self, payload, isBinary):
# if isBinary:
# print("Binary message received: {0} bytes".format(len(payload)))
# else:
# print("Text message received: {0}".format(payload.decode('utf8')))


COMMAND_USAGE = 'usage: script start|stop (download_id)'


def main(argv):
    logging.basicConfig(filename='/var/www/log.log', level=logging.DEBUG, format='%(asctime)s %(message)s',
                        datefmt='%d/%m/%Y %H:%M:%S')
    logging.debug('*** Start application ***')
    indent_log = ""

    try:
        opts, args = getopt.getopt(argv, "", [])
    except getopt.GetoptError:
        print(COMMAND_USAGE)
        exit()

    if len(args) == 0:
        print("Parameters are missing")
        print(COMMAND_USAGE)
        exit()
    else:
        # factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
        # factory.protocol = NotificationServer
        #
        # reactor.listenTCP(9000, factory)
        # reactor.run()

        # factory = WebSocketClientFactory()
        # factory.protocol = NotificationClient
        #
        # reactor.connectTCP("127.0.0.1", 8080, factory)
        # reactor.run()

        treatment = Treatment()

        # start a download
        if args[0] == 'start':
            if len(args) > 1:
                download_id = args[1]
                treatment.start_download(download_id)
            else:
                print(COMMAND_USAGE)
        # stop a download
        elif args[0] == 'stop':
            if len(args) > 1:
                download_id = args[1]
                treatment.stop_download(download_id)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'start_file_treatment':
            if len(args) > 1:
                file_path = args[1]
                treatment.start_file_treatment(file_path)
            else:
                print(COMMAND_USAGE)
        elif args[0] == 'start_multi_downloads':
            if len(args) > 1:
                file_path = args[1]
                treatment.start_multi_downloads(file_path)
        elif args[0] == 'stop_multi_downloads':
            if len(args) > 1:
                file_path = args[1]
                treatment.stop_multi_downloads(file_path)
        elif args[0] == 'check_download_alive':
            if len(args) > 1:
                download_id = args[1]
                treatment.check_download_alive(download_id)
            else:
                treatment.check_multi_downloads_alive()
        else:
            print(COMMAND_USAGE)

        treatment.disconnect()

        # close websocket ???


if __name__ == "__main__":
    main(sys.argv[1:])
