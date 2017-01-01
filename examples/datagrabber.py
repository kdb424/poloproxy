#!/usr/bin/env python
"""
    Grabs data for a currency pair
"""
import argparse
import os
import subprocess
from gc import collect
import sqlite3 as lite
import pandas as pd
import yaml
import msgpack as mp
import nanomsg
from mkdir_p import mkdir_p
import pendulum


def parse_args():
    """Parses Arguments"""
    parser = argparse.ArgumentParser(
        description='Grabs data for a currency pair')
    parser.add_argument('-c', '--currency',
                        help='Currency Pair. Example BTC_XMR',
                        required=True)
    parser.add_argument('-m', '--memory',
                        help='Memory limit in MB Default 2048, Minimum 2048',
                        dest='mem',
                        default=2048,
                        required=False)
    parser.add_argument('-s', '--start',
                        help='Start time',
                        dest='start_time',
                        default=pendulum.now().subtract(months=12),
                        required=False)
    parser.add_argument('-e', '--end',
                        help='End time',
                        dest='end_time',
                        default=pendulum.now(),
                        required=False)
    parser.add_argument('-t', '--time',
                        help='Time period. Example=1w',
                        default=None,
                        dest='time')
    return parser.parse_args()


def write_data(data):
    '''Writes data to disk'''
    print('Converting to dataframe')
    df = pd.DataFrame(data)
    df.set_index('tradeID', inplace=True)
    con = lite.connect('{}/poloticks{}_{}.db'.format(DBDIR, COIN, ALTCOIN))
    print('Writing to disk and clearing memory.')
    pd.DataFrame(data).to_sql(
        name='ticks', con=con,
        schema=None, if_exists='append', index=True,
        chunksize=None, dtype=None)



def memory_usage_ps():
    '''Returns memory usage of this process'''
    out = subprocess.Popen(
        ['ps', 'v', '-p', str(os.getpid())],
        stdout=subprocess.PIPE).communicate()[0].split(b'\n')
    vsz_index = out[0].split().index(b'RSS')
    mem = float(out[1].split()[vsz_index]) / 1024
    return mem



if __name__ == '__main__':
    ARGS = parse_args()
    CURRENCIES = ARGS.currency
    COIN, ALTCOIN = CURRENCIES.split('_')
    START_TIME = ARGS.start_time
    END_TIME = ARGS.end_time
    CONFIG_NAME = 'poloniex.cfg'

    if ARGS.time:
        TIMENUM = int(ARGS.time[:-1])
        TIMEL = ARGS.time[-1:]
        if TIMEL is 'd':
            START_TIME = pendulum.now().subtract(days=TIMENUM)
        elif TIMEL is 'w':
            START_TIME = pendulum.now().subtract(weeks=TIMENUM)
        elif TIMEL is 'm':
            START_TIME = pendulum.now().subtract(months=TIMENUM)
        elif TIMEL is 'y':
            START_TIME = pendulum.now().subtract(years=TIMENUM)

    START = START_TIME
    ADD_HOURS = 48
    END = START.add(hours=ADD_HOURS)
    # Agressive downscaling for peak times
    FAILED_ATTEMPTS = 0

    MEM = float(ARGS.mem)
    if MEM < 2048:
        MEM = float(2048)

    ERASE_LINE = '\x1b[2K'
    DBDIR = 'databases'
    mkdir_p(DBDIR)
    ALL_DATA = []

    SOCKPROXY = nanomsg.Socket(nanomsg.REQ)
    XDG_RUNTIME_DIR = os.environ.get('XDG_RUNTIME_DIR', '/tmp')
    OUR_RUNTIME_DIR = '{}/{}/{}'.format(XDG_RUNTIME_DIR, 'krypto', CONFIG_NAME)
    mkdir_p(OUR_RUNTIME_DIR)
    POLOPROXY = SOCKPROXY.connect('ipc://{}/proxy'.format(OUR_RUNTIME_DIR).encode('utf-8'))

    os.system('cls' if os.name == 'nt' else 'clear')
    # TODO Add a catch up function Currenly only works for new DB's and will duplicate data.
    while START < END_TIME:
        END = START.add(hours=ADD_HOURS)
        MSG = mp.packb(['market_trade_hist', [COIN, ALTCOIN, START.timestamp, END.timestamp]])
        SOCKPROXY.send(MSG)
        DATA = mp.unpackb(SOCKPROXY.recv(), use_list=True, encoding='UTF-8')
        ALL_DATA.extend(DATA)
        print('Data length: {} Hours grabbed: {} Failed attempts: {}'.format(
            len(DATA), ADD_HOURS, FAILED_ATTEMPTS))
        if len(DATA) < 50000:
            ADD_HOURS += 1
            START = END
            FAILED_ATTEMPTS = 0
        else:
            FAILED_ATTEMPTS += 1
            ADD_HOURS -= (3 * FAILED_ATTEMPTS)
            if ADD_HOURS < 1:
                ADD_HOURS = 1

        if memory_usage_ps() > MEM:
            write_data(ALL_DATA)
            del ALL_DATA[:]
            collect()

    write_data(ALL_DATA)
    print('Saved to database.')
