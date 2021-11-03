# How to use it

Get an API Key from https://coinmarketcap.com/api/

run:

python main.py -k <Your key obtained from coinmarketcap>

Some optional args:

-w <filename.json> writes your portfolio to a specfied file, defualt is portfolio.json.
-r <filename.json> reads a portfolio from a specified file.

# How it works

Using your API Key -- must be specified via CLI or hardcoded in if you prefer -- queries coinmarket cap 
for the top 100 coins by market cap. Randomly selects one of the coins and buys a random amount between a specified limit.
Once you have one holding it will roll the die to randomly select a holding to sell. 

# Why make something so dumb?

I saw an article about a hampster that based off of certain movements it made would sell or buy a stock, so completely random. 
This, apparently, turned out to be quite effective, if I may note, their was a similar thing done with apes. So I created a simple portfolio
and crypto buying emulator to see how it would perform. This method probably only works in bullish market conditions
and overall holding stocks/cryptos long term is a safer and more suitable method for real life. 

If this turns out to work (some tweeking will definitely be required) I'll make something that interacts with Kraken or Binance
to actually trade stuff. I'll throw in like $50 or something and just see what happens. 

# Issues?

Have any issues? Create an issue or better yet a pull request!
