from multiprocessing.dummy import current_process
import random
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from requests import Request, Session
import json
from colorama import Fore, Style, init
import os
import time


class Portfolio:
    def __init__(self, api_key, read_portfolio_from_file, cash=10_000, stocks={}, write_portfolio_to_file='portfolio.json', trending=False):
        self.stocks = stocks
        self.cash = cash
        self.original_cash = cash
        self.trending = trending
        self.portfolio_change_one_hour_time = time.time() + 3600
        self.portfolio_change_one_day_time = time.time() + 86400
        self.url = 'https://pro-api.coinmarketcap.com'
        self.api_key = api_key
        self.headers = {
            'Accepts': 'application/json',
            'X-CMC_PRO_API_KEY': self.api_key,
        }
        self.session = Session()
        self.session.headers.update(self.headers)
        self.write_file = write_portfolio_to_file
        if read_portfolio_from_file:
            self.read_portfolio_from_file(read_portfolio_from_file)
        self.portfolio_value_one_hour = self.get_portfolio_value()
        self.portfolio_value_one_day = self.portfolio_value_one_hour

    def total_value(self):
        '''
        Returns the total value of the portfolio, does not include cash on hand.
        '''

        total = 0
        for stock in self.stocks:
            total += self.stocks[stock].get_value()
        return total

    def get_portfolio_value(self):
        '''
        Gets the current value of the portfolio.
        '''
        self.update_stock_info()
        return self.total_value() + self.cash

    def get_stocks(self):
        '''
        Queries coinmarketcap api for the price of the top 100 cryptos and returns a list of cryptos.
        If trending is set to true, it will return the top 100 trending cryptos, considering you have the right api plan, untested.
        If trending is false, returns the top 100 cryptos by market cap.
        '''
        if self.trending:
            parameters = {
                'convert': 'USD',
            }
            response = self.session.get(
                self.url + '/v1/cryptocurrency/trending/most-visited', params=parameters)
            print(response.json())
            results = response.json()['data']
            cryptos = {}
            for i in results:
                cryptos[i['symbol']] = i['quote']['USD']['price']
            return cryptos
        else:
            parameters = {
                'convert': 'USD',
                'cryptocurrency_type': 'coins'
            }
            response = self.session.get(
                self.url + '/v1/cryptocurrency/listings/latest', params=parameters)
            results = response.json()['data']
            cryptos = {}
            for i in results:
                cryptos[i['symbol']] = i['quote']['USD']['price']
            return cryptos

    def buy_stock(self, stock):
        '''
        Buys the given stock.
        '''

        self.cash -= stock.get_value()
        if self.stocks.get(stock.symbol):
            self.stocks[stock.symbol].shares += stock.shares
        else:
            self.stocks[stock.symbol] = stock
        self.write_portfolio_to_file()

    def sell_random_stock(self):
        '''
        Sells a random stock that is currently owned by first getting the new value of all stocks then selling the stock to be sold.
        '''
        self.update_stock_info()
        stock = self.stocks[random.choice(list(self.stocks.keys()))]
        self.cash += stock.get_value()
        del self.stocks[stock.symbol]
        self.write_portfolio_to_file()

    def write_portfolio_to_file(self):
        '''
        Writes the portfolio to a json file.
        '''
        if time.time() >= self.portfolio_change_one_hour_time:
            # Get portfolio change one hour
            temp = self.get_portfolio_value()
            self.portfolio_change_one_hour = (
                (temp - self.portfolio_value_one_hour) / self.portfolio_value_one_hour) * 100
        elif time.time() >= self.portfolio_change_one_day_time:
            # Get portfolio change one day
            temp = self.get_portfolio_value()
            self.portfolio_change_one_day = (
                (temp - self.portfolio_value_one_day) / self.portfolio_value_one_day) * 100
        with open(self.write_file, "w", encoding='utf-8') as file:
            dict_to_write = {}
            for i in self.stocks:
                dict_to_write[i] = self.stocks[i].__dict__
            dict_to_write['cash'] = self.cash
            json.dump(dict_to_write, file, indent=4)

    def read_portfolio_from_file(self, file_name):
        '''
        Reads the portfolio from a given json file.
        '''
        with open(file_name, "r", encoding='utf-8') as file:
            dict_to_read = json.load(file)
            for i in dict_to_read:
                if i == 'cash':
                    self.cash = dict_to_read[i]
                else:
                    self.stocks[i] = Stock(
                        dict_to_read[i]['symbol'], dict_to_read[i]['shares'], dict_to_read[i]['price'])
            self.update_stock_info()
            print(self)

    def update_stock(self, symbol):
        '''
        returns a list of stocks that match the given symbol(s).
        '''
        parameters = {
            'symbol': symbol,
            'convert': 'USD'
        }
        try:
            response = self.session.get(
                self.url + '/v1/cryptocurrency/quotes/latest', params=parameters)
            results = response.json()['data']
            return results
        except Exception as e:
            print(response.json())
            print(symbol)
            raise e

    def update_stock_info(self):
        '''
        Updates the price of all stocks owned in the portfolio.
        '''

        if len(self.stocks) == 0:
            return

        cryptos_to_update = ""
        for stock in self.stocks:
            cryptos_to_update += self.stocks[stock].symbol + ","
        cryptos_to_update = cryptos_to_update[:-1]
        print(cryptos_to_update)
        results = self.update_stock(cryptos_to_update)
        for stock in self.stocks:
            for result in results:
                if result == self.stocks[stock].symbol:
                    self.stocks[stock].price = results[result]['quote']['USD']['price']
                    self.stocks[stock].set_percent_change()

    def get_best_stock(self):
        '''
        From the current portfolio, get the best performing stock by percent change since it was bought. Note: not over 24hr period.
        '''

        best_stock = Stock("", 0, 0)
        best_stock.percent_change = -101
        for stock in self.stocks:
            if best_stock == None:
                best_stock = self.stocks[stock]
            elif self.stocks[stock].percent_change > best_stock.percent_change:
                best_stock = self.stocks[stock]
        return best_stock

    def get_worst_stock(self):
        '''
        From the current portfolio, get the worst performing stock by percent change since it was bought. Note: not over 24hr period.
        '''
        worst_stock = Stock("", 0, 0)
        worst_stock.percent_change = 10_000_000_000
        for stock in self.stocks:
            if worst_stock == None:
                worst_stock = self.stocks[stock]
            elif self.stocks[stock].percent_change < worst_stock.percent_change:
                worst_stock = self.stocks[stock]
        return worst_stock

    def __str__(self):
        return str(f"{len(self.stocks)} coins owned with a total value of {self.total_value()} with ${self.cash} cash on hand and a total portfolio value of {self.total_value() + self.cash}.")

    def print_portfolio(self):
        '''
        Just prints the portfolio in pretty colors and stuff.
        '''

        # Sum original prices
        sum_ = 0
        for stock in self.stocks:
            sum_ += self.stocks[stock].original_price * \
                self.stocks[stock].shares

        original_portfolio_value = sum_
        current_portfolio_value = self.total_value()

        # Get percent change
        percent_change = (current_portfolio_value -
                          original_portfolio_value) / original_portfolio_value * 100

        os.system('clear')
        print("Cash: $" + (Fore.GREEN + str(self.cash) + Style.RESET_ALL))
        print("Portfolio Value: $" + Fore.GREEN +
              str(current_portfolio_value + self.cash) + Style.RESET_ALL)
        print("Portfolio Change: " + (Fore.GREEN if percent_change > 0 else Fore.RED) +
              str(percent_change) + "%" + Style.RESET_ALL + "%")
        print("Best performing stock: " + Fore.BLUE + self.get_best_stock().symbol + ", " + Fore.GREEN + str(self.get_best_stock(
        ).percent_change) + Style.RESET_ALL + "%, $" + Fore.GREEN + str(self.get_best_stock().get_value()) + Style.RESET_ALL)
        print("Worst performing stock: " + Fore.RED + self.get_worst_stock().symbol + ", " + Fore.RED + str(self.get_worst_stock(
        ).percent_change) + Style.RESET_ALL + "%, $" + Fore.RED + str(self.get_worst_stock().get_value()) + Style.RESET_ALL)
        print("\n")
        print("SYM\t SHRS\t \t\tPRICE \t\t\tVALUE \t\t\tCHANGE INITIAL")
        print("-------------------------------------------------------------------------------------------------------")
        for stock in self.stocks:
            self.stocks[stock].print_stock()
        print("-------------------------------------------------------------------------------------------------------\n")


class Stock:
    def __init__(self, symbol, shares, price):
        self.symbol = symbol
        self.shares = shares
        self.price = price
        self.original_price = price
        self.percent_change = 0

    def get_value(self,):
        return self.shares * self.price

    def set_percent_change(self):
        self.percent_change = (
            (self.price - self.original_price) / self.original_price) * 100

    def print_stock(self):
        print(self.symbol + ":\t" + str(self.shares) + "\t$" + str(self.price) + "\t$" + Fore.BLUE + str(self.get_value())
              + Style.RESET_ALL + "\t" + Fore.GREEN + f"{self.percent_change:.2f}" + Style.RESET_ALL + "%")
