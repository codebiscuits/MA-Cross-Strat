import backtrader as bt

class MaCross(bt.Strategy):

    params = (
        ('strat_name', 'macross'),
        ('ma_periods', 60),
        ('vol_mult', 1),
        ('pos_size', 99),
        ('start', 0),
        ('debug', False),
        )
    
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        #print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.ema = bt.ind.EMA(self.data.close, period=self.params.ma_periods)
        self.sma = bt.ind.SMA(self.data.close, period=self.params.ma_periods)
        self.roc = bt.ind.ROC(self.data.close, period=1)
        self.volatil = bt.ind.StdDev(self.roc, period=self.params.ma_periods)
        self.buysig = bt.ind.CrossOver(self.ema, self.sma)
        self.sellsig = bt.ind.CrossOver(self.sma, self.ema)
        self.stop_band = self.params.vol_mult * self.volatil * 0.01
        
    
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Nothing to do since order was submitted/accepted to/by broker
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))
    
    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        if self.buysig and not self.position:

            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.order = self.buy()
            self.order = self.sell(exectype=bt.Order.StopTrail, trailpercent=self.stop_band)

        elif self.sellsig and not self.position:

            self.log('SELL CREATE, %.2f' % self.dataclose[0])
            self.order = self.sell()
            self.order = self.buy(exectype=bt.Order.StopTrail, trailpercent=self.stop_band)

        elif self.buysig and self.position:

            if self.position.size < 0:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()
                self.order = self.buy()
                self.order = self.sell(exectype=bt.Order.StopTrail, trailpercent=self.stop_band)

        elif self.sellsig and self.position:

            if self.position.size > 0:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()
                self.order = self.sell()
                self.order = self.buy(exectype=bt.Order.StopTrail, trailpercent=self.stop_band)
