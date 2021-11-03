import random
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from requests import Request, Session
import json

class Portfolio:
    def __init__(self, api_key, read_portfolio_from_file,cash=10_000, stocks={}, write_portfolio_to_file='portfolio.json'):
        self.stocks = stocks
        self.cash = cash
        self.url = 'https://pro-api.coinmarketcap.com'
        self.api_key = '06b26ee1-737d-48ad-bd50-b9a770e1fc6e'
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        self.session = Session()
        self.session.headers.update(self.headers)
        self.write_file = write_portfolio_to_file
        if read_portfolio_from_file:
            self.read_portfolio_from_file(read_portfolio_from_file)

    def total_value(self):
        total = 0
        for stock in self.stocks:
            total += self.stocks[stock].get_value()
        return total

    def buy_stock(self, stock):
        self.cash -= stock.get_value()
        if self.stocks.get(stock.symbol):
            self.stocks[stock.symbol].shares += stock.shares
        else:
            self.stocks[stock.symbol] = stock
        print(f"Bought {stock.shares} of {stock.symbol} @ {stock.price}")
        self.write_portfolio_to_file()
    
    def sell_random_stock(self):
        '''
        Sells a random stock that is currently owned by first getting the new value of all stocks then selling the stock to be sold. 
        '''
        self.update_stock_info()
        stock = self.stocks[random.choice(list(self.stocks.keys()))]
        print(f"Sold {stock.shares} of {stock.symbol} @ {stock.price}")
        self.cash += stock.get_value()
        del self.stocks[stock.symbol]
        self.write_portfolio_to_file()

    def write_portfolio_to_file(self):
        with open(self.write_file, "w", encoding='utf-8') as file:
            dict_to_write = {}
            for i in self.stocks:
                dict_to_write[i] = self.stocks[i].__dict__
            dict_to_write['cash'] = self.cash
            json.dump(dict_to_write, file, indent=4)

    def read_portfolio_from_file(self, file_name):
        with open(file_name, "r", encoding='utf-8') as file:
            dict_to_read = json.load(file)
            for i in dict_to_read:
                if i == 'cash':
                    self.cash = dict_to_read[i]
                else:
                    self.stocks[i] = Stock(dict_to_read[i]['symbol'], dict_to_read[i]['shares'], dict_to_read[i]['price'])
            self.update_stock_info()
            print(self)

    def update_stock_info(self):
        '''
        Updates the price of all stocks owned in the portfolio.        
        '''
        cryptos_to_update = ""
        for stock in self.stocks:
            cryptos_to_update += self.stocks[stock].symbol + ","
        cryptos_to_update = cryptos_to_update[:-1]
        print(cryptos_to_update)
        response = None
        parameters = {
            'symbol': cryptos_to_update,
            'convert': 'USD'
        }
        try: 
            response = self.session.get(self.url + '/v1/cryptocurrency/quotes/latest', params=parameters)
            results = response.json()['data']
            for stock in self.stocks:
                for result in results:
                    if result == self.stocks[stock].symbol:
                        self.stocks[stock].price = results[result]['quote']['USD']['price']
            print(self)
        except Exception as e:
            print(response.json())
            print(cryptos_to_update)
            raise e
        
    
    def __str__(self):
        return str(f"{len(self.stocks)} coins owned with a total value of {self.total_value()} with ${self.cash} cash on hand and a total portfolio value of {self.total_value() + self.cash}.")

class Stock:
    def __init__(self, symbol, shares, price):
        self.symbol = symbol
        self.shares = shares
        self.price = price
    
    def get_value(self,):
        return self.shares * self.price
