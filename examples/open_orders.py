#!/usr/bin/env python
"""
    Displays the open orders for a currency pair
"""
import argparse
import os
from time import sleep
import pololib
import msgpack as mp
import nanomsg
from mkdir_p import mkdir_p


def parse_args():
    """Parses Arguments"""
    parser = argparse.ArgumentParser(
        description='Displays the open orders for a currency pair')
    parser.add_argument(
        '-c', '--currency',
        help='Currency Pair. Default=BTC_POT',
        default='BTC_POT',
        required=False)
    parser.add_argument(
        '-C', '--config',
        help='Config file name',
        dest='config',
        required=False)
    return parser.parse_args()


if __name__ == '__main__':
    ARGS = parse_args()
    CURRENCIES = ARGS.currency
    COIN, ALTCOIN = CURRENCIES.split('_')
    ERASE_LINE = '\x1b[2K'

    CONFIG_NAME = 'poloniex.cfg'
    if ARGS.config:
        CONFIG_NAME = ARGS.config

    os.system('cls' if os == 'nt' else 'clear')
    while True:
        ROWS, COLUMNS = os.popen('stty size', 'r').read().split()
        pololib.connect()
        ORDERS = pololib.open_orders(COIN, ALTCOIN)

        ROWS, COLUMNS = os.popen('stty size', 'r').read().split()
        ROWS = int(ROWS) - len(ORDERS) - 4


        print('{}{:>0} {:>26} {:>1}\r'.format(
            ERASE_LINE, ALTCOIN, 'Total Trades:', len(ORDERS)))
        print('{}{:>0} {:>13} {:>11} {:>14}\r'.format(
            ERASE_LINE, 'Rate', 'Type', 'Amount:', 'Total:'))
        for i in ORDERS:
            print('{}{:>0} {:>7} {:>15} {:>15}\r'.format(
                ERASE_LINE, i['rate'], i['type'], i['amount'], i['startingAmount']))

        print('\n' * ROWS)

        sleep(1)
