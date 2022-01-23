import random
from typing import ChainMap
# import import_ipynb
from portfolio import Portfolio
from portfolio import Stock
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from requests import Request, Session
import json
import time
import sys
import argparse


parser = argparse.ArgumentParser()

# command line args
if len(sys.argv) > 1:
    parser.add_argument('-w', '--write', help='Where to write portfolio, default=portfolio.json. Usage: -w <filename.json>', default='portfolio.json')
    parser.add_argument('-r', '--read', help='Read already created portfolio. Usage -r <filename.json> ', default=None)
    parser.add_argument('-k', '--key', required=True, help='API key', default='YOUR_API_KEY')
    parser.add_argument('-c', '--chance', help='Chance of selling a holding on each action. Usage: -c <0 < integer passed in < 100', default=50, type=int)
    args = parser.parse_args()
    portfolio_file = args.write
    read_portfolio_file = args.read
    key = args.key
    chance = args.chance


api_key = key
url = 'https://pro-api.coinmarketcap.com'

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': api_key,
}

session = Session()
session.headers.update(headers)

def get_top_100_cryptos():
    parameters = {
        'convert': 'USD',
        'cryptocurrency_type': 'coins'
    }   
    try: 
        response = session.get(url + '/v1/cryptocurrency/listings/latest', params=parameters)
        results = response.json()['data']
        cryptos = {}
        for i in results:
            cryptos[i['symbol']] = i['quote']['USD']['price']
        return cryptos
    except (ConnectionError, TimeoutError, TooManyRedirects) as e:
        raise(e)


portfolio = Portfolio(api_key, read_portfolio_from_file=read_portfolio_file if read_portfolio_file is not None else False, write_portfolio_to_file=portfolio_file)

# get random crypto from crpytos dictionary

while True:
    if random.randrange(0, 100) < chance and len(portfolio.stocks) > 0:

        portfolio.sell_random_stock()

    elif portfolio.cash > 1000:

        cryptos = get_top_100_cryptos()
        crypto_to_buy = random.choice(list(cryptos.keys()))

        print(crypto_to_buy)

        cash_to_spend = random.randrange(100, 1000)
        price_of_crypto = cryptos[crypto_to_buy]
        shares = cash_to_spend / price_of_crypto

        stock = Stock(crypto_to_buy, shares, price_of_crypto)

        portfolio.buy_stock(stock)

    portfolio.print_portfolio()

    time_till_next_action = random.randrange(600, 900)
    print(f"Next action occurs in {time_till_next_action} seconds.")
    time.sleep(time_till_next_action)

# if portfolio.cash > 1000 and random.randrange(0,2) == 1:
#     cash_to_spend = random.randrange(100, 1000)
#     price_of_crypto = cryptos[crypto_to_buy]
#     shares = cash_to_spend / price_of_crypto
#     stock = Stock(crypto_to_buy, shares, price_of_crypto)
#     portfolio.buy_stock(stock)
# else:
    # portfolio.sell_random_stock()
print(portfolio)
