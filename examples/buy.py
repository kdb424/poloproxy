#!/usr/bin/env python
"""
    Buy altcoins
"""
import argparse
import os
from time import sleep
import pololib
import msgpack as mp
import nanomsg
from mkdir_p import mkdir_p
from decimal import Decimal


def parse_args():
    """Parses Arguments"""
    parser = argparse.ArgumentParser(
        description='Displays the open orders for a currency pair')
    parser.add_argument('-c', '--currency',
                        help='Currency Pair.',
                        required=True)
    parser.add_argument('-p', '--price',
                        help='Price of the Altcoin (Right coin)',
                        required=True)
    parser.add_argument('-a', '--amount',
                        help='Amount of coin you want to trade (Right coin)',
                        required=True)
    return parser.parse_args()


if __name__ == '__main__':
    # Set constants
    ARGS = parse_args()
    CURRENCIES = ARGS.currency
    COIN, ALTCOIN = CURRENCIES.split('_')
    BUYPRICE = Decimal(ARGS.price)
    AMOUNT = Decimal(ARGS.amount)


    print('Buy cost will be {} {}'.format((AMOUNT * BUYPRICE), COIN))
    CONT = input("Continue (y/N)").rstrip().lower()
    if CONT == 'y' or CONT == 'yes':
        buyorder = pololib.buy(COIN, ALTCOIN, BUYPRICE, AMOUNT)
        print('Order number: {}'.format(BUYORDER['orderNumber']))

    else:
        print('Order was not placed')
        os._exit(0)
