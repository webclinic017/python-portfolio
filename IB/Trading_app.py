# Needed code to make connection to IB app. Info from IBAPI docs.

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import ibapi.order import Order
import pandas as pd
import threading
import time


class tradingApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
        self.data = {}
        self.pos_df = pd.DataFrame(columns=['Account', 'Symbol', 'SecType', 'Currency', 'Position', 'Avg cost'])
        self.order_df = pd.DataFrame(columns=['PermId', 'ClientId', 'OrderId', 'Account', 'Symbol', 'SecType',
                                              'Exchange', 'Action', 'OrderType', 'TotalQty', 'CashQty', 'LastPrice',
                                              'AuxPrice','Status'])

    def error(self, reqId, errorCode, errorString):
        print("Error {} {} {}".format(reqId, errorCode, errorString))

    def contractDetails(self, reqId, contractDetails):
        print("reqId: {}, contract:{}".format(reqId, contractDetails))

    def historicalData(self, reqID, bar):
        if reqID not in self.data:
            self.data[reqID] = [
                {"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume}]
        else:
            self.data[reqID].append(
                {"Date": bar.date, "Open": bar.open, "High": bar.high, "Low": bar.low, "Close": bar.close,
                 "Volume": bar.volume})
            print("reqID:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(reqID, bar.date, bar.open,
                                                                                            bar.high, bar.low,
                                                                                            bar.close, bar.volume))

# define a websocket fuction that will pass into threading
def websocket_con():
    app.run()


# IB app needs to be running locally. Need to modify the port if using paper trading or(7497) live trading (7496).
app = tradingApp()
app.connect("127.0.0.1", 7497, clientId=1)
# create threading for websockets
con_thread = threading.Thread(target=websocket_con, daemon=True)
con_thread.start()
time.sleep(1)  # add latency to allow socket connection

def usTechStk(symbol, sec_type="STK", currency="USD", exchange="SMART"):
    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.currency = currency
    contract.exchange = exchange
    return contract


def histData(req_num, contract, duration, candle_size):
    app.reqHistoricalData(reqId=req_num,
                          contract=contract,
                          endDateTime='',
                          durationStr=duration,
                          barSizeSetting=candle_size,
                          whatToShow='ADJUSTED_LAST',
                          useRTH=1,
                          formatDate=1,
                          keepUpToDate=False,
                          chartOptions=[])


# store data into dataframe
def datadataframe(tickers, tradingapp_obj):
    df_dict = {}
    for ticker in tickers:
        df_dict[ticker] = pd.DataFrame(tradingapp_obj.data[tickers.index(ticker)])
        df_dict[ticker].set_index("Date", inplace=True)
    return df_dict

tickers = ["X", "CLF", "F", "EVGO", "PLUG"]
starttime = time.time()
timeout = time.time() + 60*5
while time.time() <= timeout:
    for ticker in tickers:
        histData(tickers.index(ticker), usTechStk(ticker), '2 D', '5 mins')
        time.sleep(4)
    historicalData = datadataframe(app,tickers)
