import yfinance as yf

def on_message(message):
    print("Received update:", message)

stream = yf.WebSocket()
stream.subscribe(["BTC-USD"])
stream.listen(on_message)