#!/usr/bin/env python
from twisted.internet.defer import inlineCallbacks
from autobahn.asyncio.wamp import ApplicationSession
from autobahn_autoreconnect import ApplicationRunner

import sys
import argparse
import notify2
import simpleaudio as sa

if sys.version_info[0] is 3:
    from html.parser import HTMLParser
else:
    from HTMLParser import HTMLParser


def parse_args():
    """Parses Arguments"""
    parser = argparse.ArgumentParser(
        description='Compresses downloaded data to 15 Min OHLC pairs')
    parser.add_argument(
        '-c', '--currency',
        help='Currency Pair. Example=BTC_POT',
        dest='currency',
        required=True)
    parser.add_argument(
        '-H', '--high',
        help='If price is above this price',
        dest='high',
        default=None,
        required=False)
    parser.add_argument(
        '-L', '--low',
        help='If price is below this price',
        dest='low',
        default=None,
        required=False)
    return parser.parse_args()


def notify(price):
    '''Notifies when price hit with sound and dbus notification'''
    print(price)
    notify2.init('Poloniex {}'.format(CURRENCIES))
    n = notify2.Notification(
        '{}'.format(CURRENCIES),
        'Current price {}'.format(price),
        )
    n.show()

    wave_obj = sa.WaveObject.from_wave_file("media/ding.wav")
    play_obj = wave_obj.play()
    play_obj.wait_done()

class SubscribeTicks(ApplicationSession):
    @inlineCallbacks
    def onJoin(self, details):
        h = HTMLParser()
        self.alter = True
        def onTick(*args):
            try:
                # args variables are
                # currencyPair, last, lowestAsk, highestBid, percentChange,
                # baseVolume, quoteVolume, isFrozen, 24hrHigh, 24hrLow
                if args[0] == CURRENCIES:
                    last = args[1]
                    if float(last) > HIGH or float(last) < LOW:
                        notify(last)

            except IndexError: # Sometimes its a banhammer!
                pass

        yield self.subscribe(onTick, 'ticker')

def subscribe():
    subscriber = ApplicationRunner(u"wss://api.poloniex.com:443", u"realm1")
    subscriber.run(SubscribeTicks)


if __name__ == "__main__":
    ARGS = parse_args()
    CURRENCIES = ARGS.currency
    if ARGS.low and ARGS.high:
        HIGH = float(ARGS.high)
        LOW = float(ARGS.low)
    elif ARGS.low:
        HIGH = float(9999999)
        LOW = float(ARGS.low)
    elif ARGS.high:
        HIGH = float(ARGS.high)
        LOW = float(0)
    else:
        print('Please specify a high and or a low value')
        sys.exit()

    subscribe()
