#!/usr/bin/env python
"""
Does the thing
"""
import argparse
import os
from time import sleep
import nanomsg
import pendulum
import msgpack as mp
from mkdir_p import mkdir_p
import sys

class ParsePendulum(argparse.Action):
    """Parses pendulum types"""
    def __call__(self, parser, namespace, values,
                 option_string=None, **kwargs):
        setattr(namespace, self.dest, pendulum.parse(values))


def time_comps(time_locks, recv_time):
    """Returns the oldest time in timelocks"""
    oldest_time = time_locks[0]
    diff_time = (recv_time - oldest_time).total_seconds()
    return diff_time


def run():
    print('Running poloproxytimer')
    SOCK = nanomsg.Socket(nanomsg.REP)
    XDG_RUNTIME_DIR = os.environ.get('XDG_RUNTIME_DIR', '/tmp')
    OUR_PROXY_DIR = '{}/{}'.format(XDG_RUNTIME_DIR, 'krypto')
    mkdir_p(OUR_PROXY_DIR)
    ENDPOINT = SOCK.bind('ipc://{}/proxytimer'.format(OUR_PROXY_DIR))

    START_NOW = pendulum.now().subtract(hours=1)  # Prevents blocking at start
    TIME_LOCKS = [START_NOW] * 6
    THROTTLE = 1  # In seconds
    MSG = ''
    ERROR = None

    IS_BLOCKED = False
    while True:
        MSG = SOCK.recv().decode('UTF-8')
        if MSG == "Ok":
            RECV_TIME = pendulum.now()
            TIME_DIFF = time_comps(TIME_LOCKS, RECV_TIME)
            if TIME_DIFF < THROTTLE:
                IS_BLOCKED = True
            TIME_LOCKS.pop(0)
            TIME_LOCKS.append(RECV_TIME)
            RESP = mp.packb([IS_BLOCKED, TIME_DIFF, ERROR])
            if IS_BLOCKED:
                sleep(THROTTLE - TIME_DIFF)
                IS_BLOCKED = False
            try:
                SOCK.send(RESP)
            except Exception as e:
                print("Error responding: {}".format(e))
        else:
            try:
                RESP = mp.packb(Error = True)
                SOCK.send(RESP)
            except Exception as e:
                print("Error responding: {}".format(e))


if __name__ == '__main__':
    pid = str(os.getpid)
    pidfile = '/tmp/poloproxytimer.pid'
    if os.path.isfile(pidfile):
        print('Process appears to be running')
        sys.exit()
    with open(pidfile, 'w') as ppt:
        ppt.write(pid)
    try:
        run()
    except KeyboardInterrupt:
        os.unlink(pidfile)
