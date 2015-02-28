#!/usr/bin/python
__author__ = 'andrew'

#This will be upgraded to support the notion of multiplexing connections.
#For the time being one connection equals one service.

import websocket

def init(host, port, processid, encoding, secure, onmsg, onerror, onopen, onclose):
    websocket.enableTrace(True)
    wsprefix="ws"
    if secure: wsprefix+="s"
    hosturl=wsprefix+"://"+host+":"+str(port)+"/server/?pending="+processid+"&encoding="+encoding
    print hosturl
    ws = websocket.WebSocketApp(hosturl,
                                on_message = onmsg,
                                on_error = onerror,
                                on_close = onclose)
    ws.on_open = onopen
    ws.run_forever()


if __name__ == '__main__':
    host="ec2-54-68-145-140.us-west-2.compute.amazonaws.com"
    port=8001
    processid="1234567890"
    encoding="json"
    secure=False
    def onmsg(ws, msg):
        print "on msg on client:"+str(msg)
    def onerror(ws, err):
        print "error on client:"+str(err)
    def onopen(ws):
        print "open on client"
    def onclose(ws):
        print "closing on client"
    init(host, port, processid, encoding, secure, onmsg, onerror, onopen, onclose)



