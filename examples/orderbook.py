#!/usr/bin/env python
"""
    Displays the orderbook for a currency pair
"""
import argparse
from colorama import Fore, Style
import os
from time import sleep
import msgpack as mp
import nanomsg
from mkdir_p import mkdir_p
import pololib
import yaml


def parse_args():
    """Parses Arguments"""
    parser = argparse.ArgumentParser(
        description='Displays the orderbook for a currency pair')
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

    CONFIG_NAME = 'poloniex.cfg'
    if ARGS.config:
        CONFIG_NAME = ARGS.config

    ERASE_LINE = '\x1b[2K'

    while True:
        ROWS, COLUMNS = os.popen('stty size', 'r').read().split()
        ROWS = int(ROWS) - 3

        ORDERS = pololib.open_orders(COIN, ALTCOIN)

        BOOK = pololib.orderbook(COIN, ALTCOIN, ROWS)

        print('{:>14}{:>21}{:>15}\r'.format('Asks:', ALTCOIN, 'Bids:'))
        print('{:>0}{:>20}{:>16}{:>18}\r'.format(
            'Rate', 'Amount', 'Rate', 'Amount'))
        for ask, bid in zip(BOOK['asks'], BOOK['bids']):
            if any(ask[0] in x.values() for x in ORDERS):
                print('{}{}{}{:>19}{}'.format(
                    ERASE_LINE, Fore.RED, ask[0], ask[1], Style.RESET_ALL), end='')
            else:
                print('{}{:>0}{:>19}'.format(ERASE_LINE, ask[0], ask[1]), end='')

            if any(bid[0] in x.values() for x in ORDERS):
                print('{}{:>14}{:>18}'.format(Fore.GREEN, bid[0], bid[1]))

            else:
                print('{:>14}{:>18}'.format(bid[0], bid[1]))

            print(Style.RESET_ALL, end='')
        sleep(.5)
