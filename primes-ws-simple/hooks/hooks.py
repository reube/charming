#!/usr/bin/python
#
# Copyright 2014 - INSERT proper header here
#
# Authors:
#  Andrew Farrell <ahfarrell@sparkl.com>
#
# Version 0.1

"""
Hooks module for primes example charm
"""

import sys
import os

charmdir = os.environ['CHARM_DIR']
libpath=os.path.join(charmdir, 'lib')
sys.path.insert(0, libpath)

from charmhelpers.core.hookenv import (
    log,
    Hooks,
    UnregisteredHookError,
    open_port
)
from charmhelpers.fetch import (
    apt_update,
    apt_install,
    config
)
from charmhelpers.utils import (
    execthis
)

s_routerhost='routerhost'
s_hostport='hostport'
s_origreplyto="origreplyto"
s_serviceport="serviceport"

hooks = Hooks()

@hooks.hook('install')
def install():
   log('begin...install hook')

   #
   log('installing pip')
   apt_update(fatal=True)
   apt_install('python-pip', fatal=True)

   #
   log('installing tornado')
   execthis('pip install tornado')

   #
   log('installing websocket-client')
   execthis('pip install websocket-client')

   log('done...install hook')

@hooks.hook('config-changed')
def config_changed():
    log('begin...config-changed hook')

    myconfig= config()
    routerhost=str(myconfig[s_routerhost])
    hostport=str(myconfig[s_hostport])
    origreplyto=str(myconfig[s_origreplyto])
    serviceport=str(myconfig[s_serviceport])

    open_port(serviceport)

    execthis('python lib/primes/__init__.py ' +
             routerhost+' ' +
             hostport+' ' +
             origreplyto+' nil nil nil '+
             libpath+' &')

    log('done...config-changed hook')



if __name__ == '__main__':
    try:
        hooks.execute(sys.argv)
    except UnregisteredHookError as e:
        log('Unknown hook {} - skipping.'.format(e))

