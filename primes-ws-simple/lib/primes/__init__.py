#!/usr/bin/python
__author__ = 'andrew'

import logging
import json
import os
import sys
from time import sleep

now='latest'
logging.basicConfig(filename='/tmp/container-info.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s line:%(lineno)d',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

args=sys.argv

if len(args)==7:
    #this is not running inside a charm...
    libpath=os.path.realpath("/init.py").replace("/primes/__init__.py","")
elif len(args)==8:
    #this is running inside a charm...i.e. we pass the charmdir as an additional argument..
    libpath=args[7]
else:
    logger.error("wrong number of arguments at: "+len(args))

logger.debug("libpath..."+libpath)
sys.path.insert(0, libpath)

host=args[1]
port=args[2]
processid=args[3]
serviceport_ignored=args[4]
encoding='json'
secure=False

s_openevent = 'open-event'
s_request = 'request-event'
s_reply = 'reply-event'
s_tag = 'tag'
s_content = 'content'
s_attributes='attr'
s_op_rr = 'request-reply'
s_op_sr = "solict-response"
s_op_ow = 'one-way'
s_op_no = 'notification'
s_id='id'
s_opid='opId'
s_name='name'
s_replyTo='replyTo'
s_instanceid='instanceId'
s_outputname='outputName'
s_fieldtag='field'
s_msgid='_msgid'
s_output='output'
s_replytag='reply'
s_errtag='error'
s_reason='reason'

opids={}
opnames={}
fieldids={}
fieldnames={}


def on_message(ws, message):
    msgasjson=json.loads(message)
    logger.debug(msgasjson)
    logger.debug(type(msgasjson))

    eventname=msgasjson.get(s_tag)
    eventattrs=msgasjson.get(s_attributes)
    eventcontent=msgasjson.get(s_content)

    logger.debug(eventname)
    logger.debug(eventattrs)
    logger.debug(eventcontent)

    if eventname==s_openevent:
       handle_openevent(eventcontent)
    elif eventname==s_request:
       response=handle_request(eventattrs, eventcontent)
       logger.info(response)
       ws.send(response)
    else:
       logger.debug("ignoring "+str(eventname)+","+str(message))


#this should be moved to a lib...
def encode_as_json_list(replyTo, outputname, fields):

    logger.debug(str(outputname))
    logger.debug(str(fields))

    #content
    contentmap={}
    for field in fields.keys():
        contentmap[field]=fields.get(field)

    encoding = {s_tag:s_replytag,
                s_replyTo: replyTo,
                s_msgid:'ignore',
                s_outputname: outputname,
                s_output:contentmap}

    return json.dumps(encoding)


def handle_openevent(eventcontent):

    for item in eventcontent:
        itemtag = item.get(s_tag)
        logger.debug(itemtag)
        attrs = item.get(s_attributes)
        logger.debug(attrs)

        itemid = attrs.get(s_id)
        itemname = attrs.get(s_name)

        if itemtag==s_op_rr or itemtag==s_op_ow or itemtag==s_op_sr or itemtag==s_op_no :
            logger.debug('adding op...'+itemid+":"+itemname)
            opids[itemid]=itemname
            opnames[itemname]=itemid

        elif itemtag==s_fieldtag :
            logger.debug('adding field...'+itemid+":"+itemname)
            fieldids[itemid]=itemname
            fieldnames[itemname]=itemid

def handle_request(eventattrs, eventcontent):

    opid = eventattrs.get(s_opid)
    opname = opids.get(opid)
    logger.debug(opid)
    logger.debug(opname)

    replyTo = eventattrs.get(s_replyTo)
    logger.debug(replyTo)

    fields={}
    for item in eventcontent:
        itemattrs = item.get(s_attributes)
        itemcontent = item.get(s_content)
        logger.debug(itemattrs)
        logger.debug(itemcontent)

        fieldname=itemattrs.get(s_id)
        fieldvalue=itemcontent[0]
        fields[fieldname]=fieldvalue

    fieldkeys=fields.keys()
    logger.debug(fieldkeys)
    if len(fieldkeys)>0:
        if str(fieldkeys[0]).startswith('F-'):  #this should always be the case
            #we need to convert to field names...
            idfields=fields
            fields={}

            for fieldkey in fieldkeys:
                fieldname=fieldids.get(fieldkey)
                fieldval=idfields.get(fieldkey)
                fields[fieldname]=fieldval

    logger.debug(str(fields))
    if opname=="FirstDivisor":
        return handle_fd(replyTo)
    elif opname=="Test":
        return handle_test(replyTo, fields)
    elif opname=="Iterate":
        return handle_iterate(replyTo, fields)
    else:
        return handle_error(replyTo,"invalid_opname")


def handle_fd(replyTo):
    return encode_as_json_list(replyTo, 'Divisor', {fieldnames.get('div'): 2})


def handle_iterate(replyTo, args):
    n = int(args.get('n'))
    div=int(args.get('div'))

    if div==2:
        res=3
    else:
        res=div+2

    return encode_as_json_list(replyTo, 'Iterate', {fieldnames.get('div'): res, fieldnames.get('n'): n})

def handle_test(replyTo, args):
    n = int(args.get('n'))
    div=int(args.get('div'))
    square=div*div
    rem=n % div

    if square>n:
        output="Yes"
        field="YES"
    elif rem==0:
        output="No"
        field="NO"
    else:
        output="Maybe"
        field="MAYBE"

    return encode_as_json_list(replyTo, output, {fieldnames.get(field): field})


def handle_error(replyTo, reason):
    encoding = {s_tag:s_errtag,
                s_replyTo: replyTo,
                s_reason: reason}

    return json.dumps(encoding)

def on_error(ws, error):
    logger.error(error)

def on_close(ws):
    logger.info("### closed websocket on: "+host)

def on_open(ws):
    logger.info("### open websocket on: "+host)


import websock

try:
    websock.init(
        host,
        port,
        processid,
        encoding,
        secure,
        on_message,
        on_error,
        on_open,
        on_close
    )
except Exception as e:
    logger.error(str(e))
