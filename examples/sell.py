#!/usr/bin/env python
"""
    Sell altcoins
"""
import argparse
from decimal import Decimal
import nanomsg
import os
import pololib
from mkdir_p import mkdir_p
import msgpack as mp
from time import sleep


def parse_args():
    """Parses Arguments"""
    parser = argparse.ArgumentParser(
        description='Displays the open orders for a currency pair')
    parser.add_argument(
        '-c', '--currency',
        help='Currency Pair.',
        required=True)
    parser.add_argument(
        '-p', '--price',
        help='Price of the Altcoin (Right coin)',
        required=True)
    parser.add_argument(
        '-a', '--amount',
        help='Amount of coin you want to trade (Right coin)',
        required=True)
    parser.add_argument(
        '-C', '--config',
        help='Config file name',
        dest='config',
        required=False)
    return parser.parse_args()


if __name__ == '__main__':
    # Set constants
    ARGS = parse_args()
    CURRENCIES = ARGS.currency
    COIN, ALTCOIN = CURRENCIES.split('_')
    SELLPRICE = Decimal(ARGS.price)
    AMOUNT = Decimal(ARGS.amount)

    CONFIG_NAME = 'poloniex.cfg'
    if ARGS.config:
        CONFIG_NAME = ARGS.config

    print('Sell price will be {} {}'.format((AMOUNT * SellPRICE), COIN))
    CONT = input("Continue (y/N)").rstrip().lower()
    if CONT == 'y' or CONT == 'yes':
        SELLORDER = pololib.sell(COIN, ALTCOIN, SELLPRICE, AMOUNT)
        print('Order number: {}'.format(SELLORDER['orderNumber']))

    else:
        print('Order was not placed')
        os._exit(0)
