import json
import os
import queue
import socket
import sys
import tornado

from threading import Thread
from tornado.ioloop import IOLoop
from tornado import gen
from tornado.websocket import websocket_connect


voc_send_q = queue.Queue()
voc_rcv_q = queue.Queue()

class VocChannel(object):

    def __init__(self):
        token = os.getenv("VOC_COMM_TOKEN")
        host = self.my_ip()
        port = os.getenv("VOC_COMM_PORT")
        proxy = os.getenv("VOC_COMM_PROXY")
        self.url = "wss://" + proxy + "/hostip/" + host + ":" + str(port) + "/voccomm/" + token + "/client?vocmsgs=1"
        self.ws = None
        self.ioloop = IOLoop(make_current=True)
        self.connect()
        self.ioloop.start()

    def my_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 53))
        return s.getsockname()[0]

    @gen.coroutine
    def connect(self):
        print("VOC: Connecting to Vocareum Communication Server...")
        try:
            self.ws = yield websocket_connect(self.url, on_message_callback=self.receiver)
        except Exception:
            print("VOC: Error: Could not connect")
        else:
            print("VOC: Connected")
            self.sender()

    def receiver(self, msg):
        # print("DBG RCVR: MAYBE Adding to Q: {}".format(msg))
        if msg is None:
            print("VOC: ERROR: Vocareum Connection closed")
        try:
            js = json.loads(msg)
            if 'voc' in js:
                if 'severity' in js and js['severity'] == "ERROR":
                    if 'msg' in js and js['msg'] is not None:
                        print("VOC: ERROR: {}".format(js['msg']))
                return
        except: # Exception as e: # json.decoder.JSONDecodeError
            # not vocareum json - should be a real message 
            pass
        # print("DBG RCVR: Adding to Q: {}".format(msg))
        voc_rcv_q.put(msg)

    @gen.coroutine
    def sender(self):
        while True:
            if self.ws is not None:
                # print("VOC DBG: Sender: Wait for CMD...")
                try:
                    msg = voc_send_q.get(block=False)
                    # print("VOC DBG: Sender: Got CMD: {}".format(msg))
                except queue.Empty:
                    yield gen.sleep(0.01)
                else:
                    self.ws.write_message(msg)


class VocCommChannel(object):

    channel = None
    
    def __init__(self, read_timeout=5):
        if VocCommChannel.channel is None:
            VocCommChannel.channel = Thread(target=VocChannel)
            # VocCommChannel.channel.setDaemon(True)
            VocCommChannel.channel.start()
        self.read_timeout = read_timeout

    def read(self, block=True, timeout=None):
        if timeout is None:
            timeout = self.read_timeout
        # print("VOC DBG: Going to READ... ")
        msg = voc_rcv_q.get(block=block, timeout=timeout)
        # print("VOC DBG: Just READ: " + msg)
        return msg        

    def write(self, msg):
        # print("VOC DBG: Going to WRITE: " + msg, flush=True)
        voc_send_q.put(msg)
        # print("VOC DBG: Just WROTE: " + msg, flush=True)

            
    

