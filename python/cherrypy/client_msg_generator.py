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
import random
import time
from ws4py.client.threadedclient import WebSocketClient

__author__ = "Valeriy Solovyov (weldpua2008@gmail.com)"
__copyright__ = "Copyright (C) 2015 Valeriy Solovyov"
__license__ = "MIT"
__version__ = "1.0"


class Subscriber(WebSocketClient):
    def handshake_ok(self):
        self._th.start()
        self._th.join()

    def opened(self):
        while True:
            self.send("Sending msg %d" % random.randint(0, 100))
            time.sleep(random.randint(0, 3))


    def received_message(self, m):
        print "=> %d %s" % (len(m), str(m))

if __name__ == '__main__':
    try:
        ws = Subscriber('ws://localhost:9000/ws?sessionId=sadas-asddas-dasdas-das')
        ws.connect()
    except KeyboardInterrupt:
        ws.close()