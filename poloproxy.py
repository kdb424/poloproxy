#!/usr/bin/env python
'''
Proxifies Poloniex
'''
import argparse
import os
from time import sleep, time
import nanomsg
import pendulum
import msgpack as mp
from mkdir_p import mkdir_p
import poloniex
import subprocess
import yaml


class ParsePendulum(argparse.Action):
    '''Parses pendulum types'''
    def __call__(self, parser, namespace, values,
                 option_string=None, **kwargs):
        setattr(namespace, self.dest, pendulum.parse(values))


def _return_ticker(polo):
    '''Returns ticker'''
    return polo.returnTicker().decode('UTF-8')


def _return_24h_volume(polo):
    '''Returns 24hr volume'''
    return polo.return24hVolume()


def _return_currencies(polo):
    '''Returns currencies'''
    return polo.returnCurrencies()


def _return_loan_orders(polo):
    '''Returns loan orders'''
    return polo.returnLoanOrders()


def _orderbook(polo, coin, altcoin, rows):
    '''Returns orderbook'''
    return polo.returnOrderBook('{}_{}'.format(coin.decode(
        'UTF-8'), altcoin.decode('UTF-8')), depth=rows)


def _chart_data(polo, coin, altcoin):
    '''Returns chart data'''
    return polo.returnChartData('{}_{}'.format(coin.decode(
        'UTF-8'), altcoin.decode('UTF-8')))


def _market_trade_hist(polo, coin, altcoin, start=time()-60, end=time()):
    '''Returns market trade history'''
    return polo.marketTradeHist('{}_{}'.format(coin.decode(
        'UTF-8'), altcoin.decode('UTF-8')), start, end)


def _return_trade_hist(polo):
    '''Returns trade history'''
    return polo.returnTradeHistory()


def _return_balances(polo):
    '''Returns balances'''
    return polo.returnBalances()


def _return_avalable_account_balances(polo):
    '''Returns avalable account balances'''
    return polo.returnBalances()


def _return_margin_account_summary(polo):
    '''Returns margin account summary'''
    return polo.returnMarginAccountSummary()


def _return_margin_position(polo):
    '''Returns margin position'''
    return polo.getMarginPosition()


def _return_complete_balances(polo):
    '''Returns complete balances'''
    return polo.returnCompleteBalances()


def _return_deposit_addresses(polo):
    '''Returns deposit addresses'''
    return polo.returnDepositAddresses()


def _open_orders(polo, coin, altcoin):
    '''Returns open trades with currency pair'''
    return polo.returnOpenOrders('{}_{}'.format(coin.decode(
        'UTF-8'), altcoin.decode('UTF-8')))


def _return_deposits_withdraws(polo):
    '''Returns deposit/withdraw history'''
    return polo.returnDepositsWithdraws()


def _return_tradable_balances(polo):
    '''Returns tradable balances'''
    return polo.returnTradableBalances()


def _return_active_loans(polo):
    '''Returns active loans'''
    return polo.returnActiveLoans()


def _return_open_loan_offers(polo):
    '''Returns open loan offers'''
    return polo.returnOpenLoanOffers()


def _return_fee_info(polo):
    '''Returns fee info'''
    return polo.returnFeeInfo()


def _return_lending_hist(polo, start=False, end=time(), limit=False):
    '''Returns lending history'''
    return polo.returnLendingHistory(start, end, limit)


def _return_order_trades(polo, ordernumber):
    '''Return trade orders'''
    return polo.returnOrderTrades(ordernumber.decode('UTF-8'))

def _create_loan_offer(polo, coin, amt, rate, autoRenew=0, duration=2):
    '''Creates a loan offer'''
    return polo.createLoanOffer(
        coin.decode('UTF-8'),
        amt,
        rate.decode,
        autoRenew,
        duration
        )

def _cancel_loan_offer(polo, ordernumber):
    '''Cancels loan offer'''
    return polo.cancelLoanOffer(ordernumber)


def _toggle_auto_renew(polo, ordernumber):
    '''Toggle autoRenew on a loan'''
    return polo.toggleAutoRenew(ordernumber)


def _close_margin_position(polo, coin, altcoin):
    '''Close a margin position'''
    return polo.closeMarginPosition('{}_{}'.format(coin.decode(
        'UTF-8'), altcoin.decode('UTF-8')))

def _margin_buy(polo, coin, altcoin, rate, amt, lendingRate=2,
                fill_or_kill=False, immediate_or_cancel=False,
                post_only=False):
    return polo.marginBuy(
        '{}_{}'.format(
            coin.decode('UTF-8'),
            altcoin.decode('UTF-8')),
        rate,
        amt,
        lendingRate
        )


def _margin_sell(polo, coin, altcoin, rate, amt, lendingRate=2):
    return polo.marginSell(
        '{}_{}'.format(
            coin.decode('UTF-8'),
            altcoin.decode('UTF-8')),
        rate,
        amt,
        lendingRate
        )


def _buy(polo, coin, altcoin, rate, amt):
    '''Buy coins'''
    return polo.buy(
        '{}_{}'.format(
            coin.decode('UTF-8'),
            altcoin.decode('UTF-8')
            ),
        rate.decode('UTF-8'),
        amt.decode('UTF-8')
    )


def _sell(polo, coin, altcoin, rate, amt):
    '''Sell coin'''
    return polo.sell(
        '{}_{}'.format(
            coin.decode('UTF-8'),
            altcoin.decode('UTF-8')
            ),
        rate.decode('UTF-8'),
        amt.decode('UTF-8')
    )


def _cancel_order(polo, ordernumber):
    '''Cancels order'''
    return polo.cancelOrder(
        ordernumber.decode('UTF-8')
        )


def _move_order(polo, ordernumber, rate, amt):
    '''Moves order'''
    return polo.moveOrder(
        ordernumber.decode('UTF-8'),
        rate.decode('UTF-8'),
        amt.decode('UTF-8'),
        )


def _withdraw(polo, coin, amt, address):
    '''Withdraws coin'''
    return polo.withdraw(
        coin.decode('UTF-8'),
        amt,
        address.decode('UTF-8')
        )

def _transfer_balance(polo, coin, amt, fromac, toac):
    '''Transfers balance'''
    return polo.transferBalances(
        coin.decode('UTF-8'),
        amt,
        fromac.decode('UTF-8'),
        toac.decode('UTF-8')
        )


def parse_args():
    '''Parses ArgumentParser'''
    parser = argparse.ArgumentParser(
        description='Poloniex proxy')
    parser.add_argument(
        '-A', '--api-key',
        help='API Key',
        dest='api_key',
        required=False)
    parser.add_argument(
        '-S', '--secret',
        help='Secret',
        dest='api_secret',
        required=False)
    parser.add_argument(
        '-D', '--debug',
        help='Debugging',
        dest='debug',
        action='store_true',
        required=False)
    parser.add_argument(
        '-C', '--config',
        help='Config file name',
        dest='config',
        required=False)
    return parser.parse_args()


def get_conf(cfg_file):
    '''Gets config file'''
    with open(cfg_file, 'r') as config:
        cfg = yaml.load(config)
        return cfg


def check_timer(socktimer):
    '''Checks timer to see if call can be sent'''
    socktimer.send('Ok'.encode('UTF-8'))
    resp = socktimer.recv()
    resp = mp.unpackb(resp, use_list=True)
    print('{}Time diff: {}s'.format(
        ERASE_LINE, round(resp[1], 2)), end='\r')
    if resp[0] is True:  # If errors
        print('{}Throttled: {}'.format(
            ERASE_LINE, round(resp[1], 2)), end='\r')
        # TODO Handle errors
    return resp


def _polowrap(key=None, secret=None):
    '''Wraps polo'''
    if key is not None and secret is not None:
        return poloniex.Poloniex(
            key,
            secret,
            extend=True,
            timeout=10,
            coach=False,
            )
    else:
        return poloniex.Poloniex(
            extend=True,
            timeout=10,
            coach=False,
            )


if __name__ == '__main__':
    ARGS = parse_args()
    KEY = None
    SECRET = None
    DEBUG = ARGS.debug
    CONFIG_NAME = 'poloniex.cfg'
    if ARGS.config:
        CONFIG_NAME = ARGS.config

    if not ARGS.api_key and not ARGS.api_secret:
        CONFIG_FILE = '{}/.config/poloproxy/{}'.format(os.path.expanduser('~'), CONFIG_NAME)
        YAML_CFG = get_conf(CONFIG_FILE)
        KEY = YAML_CFG['key']
        SECRET = YAML_CFG['secret']
    else:
        KEY = ARGS.api_key
        SECRET = ARGS.api_secret

    POLO = _polowrap(KEY, SECRET)

    ERASE_LINE = '\x1b[2K'

    pid = str(os.getpid)
    pidfile = '/tmp/{}.pid'.format(CONFIG_NAME)
    if os.path.isfile(pidfile):
        print('Process appears to be running.')
        sys.exit()
    with open (pidfile, 'w') as pf:
        pf.write(pid)
    try:
        ppt = subprocess.Popen([
            'python',
            'poloproxytimer.py']
                              )
        try:
            pass
            #ppt.wait()
        except KeyboardInterrupt:
            try:
               ppt.terminate()
            except OSError:
               pass
            ppt.wait()

        print('Running poloproxy')
        SOCKPROXY = nanomsg.Socket(nanomsg.REP)
        SOCKTIMER = nanomsg.Socket(nanomsg.REQ)

        XDG_RUNTIME_DIR = os.environ.get('XDG_RUNTIME_DIR', '/tmp')
        OUR_RUNTIME_DIR = '{}/{}/{}'.format(XDG_RUNTIME_DIR, 'krypto', CONFIG_NAME)

        OUR_PROXY_DIR = '{}/{}'.format(XDG_RUNTIME_DIR, 'krypto')
        mkdir_p(OUR_PROXY_DIR)

        POLOPROXY = SOCKPROXY.bind('ipc://{}/proxy'.format(OUR_PROXY_DIR))
        POLOPROXYTIMER = SOCKTIMER.connect('ipc://{}/proxytimer'.format(OUR_PROXY_DIR))

        MSG = []
        while True:
            MSG = SOCKPROXY.recv()
            try:
                API_CALL = mp.unpackb(MSG)
                CALL_METHOD = locals().get('_' + API_CALL[0].decode('UTF-8'))
                RESULT = CALL_METHOD(POLO, *API_CALL[1])
                SEND_BACK_RESULT = mp.packb(RESULT)
                SOCKPROXY.send(SEND_BACK_RESULT)
            except Exception as e:
                print(e)
                SOCKPROXY.send('Error parsing'.encode('UTF-8'))

    finally:
        os.unlink(pidfile)
