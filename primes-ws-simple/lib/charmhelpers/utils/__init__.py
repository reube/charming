__author__ = 'andrew'

import subprocess
import socket
from charmhelpers.core.hookenv import (
    log,
    relation_get
)

def execthis(execstr, home='export HOME=/home/ubuntu && '):
    log('executing...'+execstr)
    subprocess.call(home+execstr, shell=True)  #need to handle error

def getprivateaddress():
    return getaddress('private-address')

def getpublicaddress():
    return getaddress('publicaddress')

def getaddress(address):
    _address = str(relation_get(address))

    try:
        #Test to see if an IPv4 address
        socket.gethostbyaddr(_address)
    except socket.error:
        try:
            socket.gethostbyname(_address)
        except socket.error:
            return False, ""

    return True, _address

