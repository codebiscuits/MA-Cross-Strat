import backtrader as bt
import math

class MaCross(bt.Strategy):

    params = (
        ('strat_name', 'macross'),
        ('ma_periods', 60),
        ('vol_mult', 1),
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
        # TODO possible improvement might be to adjust roc periods as well as stdev periods to give more true measure of recent volatility. maybe set roc periods as sqrt of ma_periods
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

class MaCrossRSI(bt.Strategy):
    params = (
        ('strat_name', 'macrossrsi'),
        ('ma_periods', 60),
        ('vol_mult', 1),
        ('start', 0),
        ('debug', False),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.ema = bt.ind.EMA(self.data.close, period=self.params.ma_periods)
        self.sma = bt.ind.SMA(self.data.close, period=self.params.ma_periods)
        self.rsi = bt.ind.RelativeStrengthIndex(self.data.close)
        self.roc = bt.ind.ROC(self.data.close, period=1)
        self.volatil = bt.ind.StdDev(self.roc, period=self.params.ma_periods)
        self.buysig = bt.ind.CrossOver(self.ema, self.sma) and self.rsi <= 50
        self.sellsig = bt.ind.CrossOver(self.sma, self.ema) and self.rsi >= 50
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

class MaCrossRoot(bt.Strategy):
    params = (
        ('strat_name', 'macrossroot'),
        ('ma_periods', 60),
        ('vol_mult', 1),
        ('start', 0),
        ('debug', False),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.root_ma = round(math.sqrt(self.params.ma_periods))

        self.ema = bt.ind.EMA(self.data.close, period=self.params.ma_periods)
        self.sma = bt.ind.SMA(self.data.close, period=self.params.ma_periods)
        self.roc = bt.ind.ROC(self.data.close, period=self.root_ma)
        # TODO maybe volatil period could be adjusted by a scalar like *2 or /2 etc
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

class MaCrossFrac(bt.Strategy):
    params = (
        ('strat_name', 'macrossfrac'),
        ('ma_periods', 18000),
        ('vol_mult', 450),
        ('divisor', 30),
        ('start', 0),
        ('debug', False),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.ema = bt.ind.EMA(self.data.close, period=self.params.ma_periods)
        self.sma = bt.ind.SMA(self.data.close, period=self.params.ma_periods)
        self.roc = bt.ind.ROC(self.data.close, period=round(self.params.ma_periods/self.params.divisor), plot=False)
        self.volatil = bt.ind.StdDev(self.roc, period=self.params.ma_periods, plot=False)
        self.buysig = bt.ind.CrossOver(self.ema, self.sma, plot=False)
        self.sellsig = bt.ind.CrossOver(self.sma, self.ema, plot=False)
        self.stop_band = self.params.vol_mult * self.volatil * 0.01

    def next(self):
        self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        if not self.position:
            if self.buysig:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy(size=0.01)
                self.order = self.sell(exectype=bt.Order.StopTrail, size=1, trailpercent=self.stop_band)
            elif self.sellsig:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell(size=0.01)
                self.order = self.buy(exectype=bt.Order.StopTrail, size=1, trailpercent=self.stop_band)
        else:
            if self.buysig:
                if self.position.size < 0:
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    # self.order = self.close()
                    self.order = self.buy(size=0.02)
                    self.order = self.sell(exectype=bt.Order.StopTrail, size=1, trailpercent=self.stop_band)
            elif self.sellsig:
                if self.position.size > 0:
                    self.log('SELL CREATE, %.2f' % self.dataclose[0])
                    # self.order = self.close()
                    self.order = self.sell(size=0.02)
                    self.order = self.buy(exectype=bt.Order.StopTrail, size=1, trailpercent=self.stop_band)

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

class MaCrossFracFR(bt.Strategy):
    params = (
        ('strat_name', 'macrossfrac'),
        ('ma_periods', 60),
        ('vol_mult', 1),
        ('divisor', 10),
        ('fixed_risk', 10),
        ('start', 0),
        ('debug', False),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.current_cash = self.broker.getvalue()
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.ema = bt.ind.EMA(self.data.close, period=self.params.ma_periods)
        self.sma = bt.ind.SMA(self.data.close, period=self.params.ma_periods)
        self.roc = bt.ind.ROC(self.data.close, period=round(self.params.ma_periods/self.params.divisor), plot=False)
        self.volatil = bt.ind.StdDev(self.roc, period=self.params.ma_periods, plot=False)
        self.buysig = bt.ind.CrossOver(self.ema, self.sma, plot=False)
        self.sellsig = bt.ind.CrossOver(self.sma, self.ema, plot=False)
        self.stop_band = self.params.vol_mult * self.volatil * 0.01
        self.f_size = (self.params.fixed_risk) / (self.stop_band * 100)


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

        if self.f_size > 0.99:
            self.size_limit = 0.99
        else:
            self.size_limit = self.f_size

        if self.order:
            return

        if self.buysig and not self.position:

            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.order = self.buy(size=self.size_limit)
            self.order = self.sell(exectype=bt.Order.StopTrail, size=self.size_limit, trailpercent=self.stop_band)

        elif self.sellsig and not self.position:

            self.log('SELL CREATE, %.2f' % self.dataclose[0])
            self.order = self.sell(size=self.size_limit)
            self.order = self.buy(exectype=bt.Order.StopTrail, size=self.size_limit, trailpercent=self.stop_band)

        elif self.buysig and self.position:

            if self.position.size < 0:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()
                self.order = self.buy(size=self.size_limit)
                self.order = self.sell(exectype=bt.Order.StopTrail, size=self.size_limit, trailpercent=self.stop_band)

        elif self.sellsig and self.position:

            if self.position.size > 0:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()
                self.order = self.sell(size=self.size_limit)
                self.order = self.buy(exectype=bt.Order.StopTrail, size=self.size_limit, trailpercent=self.stop_band)

        if len(self) % 1000 == 0:
            vol = self.volatil
            band = self.stop_band
            print(f'Bar: {len(self)}, Volatility: {vol[0]:.5f}, Stop Band: {band[0]:.5f}, Size: {self.size_limit}')

class MaCrossFracNew(bt.Strategy):
    params = (
        ('strat_name', 'macrossfracnew'),
        ('ma_periods', 18000),
        ('vol_mult', 450),
        ('divisor', 30),
        ('percents', 0.9),
        ('start', 0),
        ('debug', False),
    )

    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        # print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.startcash = self.broker.getvalue()
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.ema = bt.ind.EMA(self.data.close, period=self.params.ma_periods)
        self.sma = bt.ind.SMA(self.data.close, period=self.params.ma_periods)
        self.roc = bt.ind.ROC(self.data.close, period=round(self.params.ma_periods/self.params.divisor), plot=False)
        self.volatil = bt.ind.StdDev(self.roc, period=self.params.ma_periods, plot=False)
        self.buysig = bt.ind.CrossOver(self.ema, self.sma, plot=False)
        self.sellsig = bt.ind.CrossOver(self.sma, self.ema, plot=False)
        self.stop_band = self.params.vol_mult * self.volatil * 0.01

    def next(self):
        # self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        if not self.position:
            if self.buysig:
                buy_ord = self.order_target_percent(target=self.p.percents)
                try:
                    buy_ord.addinfo(name="Long Market Entry")
                    stop_size = buy_ord.size - abs(self.position.size)
                    self.sl_ord = self.sell(exectype=bt.Order.StopTrail, size=stop_size, trailpercent=self.stop_band)
                    self.sl_ord.addinfo(name='Long Stop Loss')
                    self.log(f'BUY CREATE, {self.dataclose[0]:.2f}, size = {self.position.size}')
                except AttributeError:
                    return
            if self.sellsig:
                sell_ord = self.order_target_percent(target=-self.p.percents)
                sell_ord.addinfo(name="Short Market Entry")
                stop_size = sell_ord.size - abs(self.position.size)
                self.sl_ord = self.buy(exectype=bt.Order.StopTrail, size=stop_size, trailpercent=self.stop_band)
                self.sl_ord.addinfo(name='Short Stop Loss')
                self.log(f'SELL CREATE, {self.dataclose[0]:.2f}, size = {self.position.size}')
        else:
            if self.buysig:
                if self.position.size < 0:
                    buy_ord = self.order_target_percent(target=self.p.percents, oco=self.sl_ord)
                    try:
                        buy_ord.addinfo(name="Long Market Entry")
                        stop_size = buy_ord.size - abs(self.position.size)
                        self.sl_ord = self.sell(size=stop_size, exectype=bt.Order.StopTrail, trailpercent=self.stop_band)
                        self.sl_ord.addinfo(name='Long Stop Loss')
                        self.log(f'BUY CREATE-FLIP LONG, {self.dataclose[0]:.2f}, size = {self.position.size}')
                    except AttributeError:
                        return
            if self.sellsig:
                if self.position.size > 0:
                    sell_ord = self.order_target_percent(target=-self.p.percents, oco=self.sl_ord)
                    sell_ord.addinfo(name="Short Market Entry")
                    stop_size = sell_ord.size - abs(self.position.size)
                    self.sl_ord = self.buy(size=stop_size, exectype=bt.Order.StopTrail, trailpercent=self.stop_band)
                    self.sl_ord.addinfo(name='Short Stop Loss')
                    self.log(f'SELL CREATE-FLIP SHORT, {self.dataclose[0]:.2f}, size = {self.position.size}')

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Nothing to do since order was submitted/accepted to/by broker
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, '
                         f'Price: {order.executed.price:.2f}, '
                         f'Cost: {order.executed.value:.2f}, '
                         f'Comm: {order.executed.comm:.2f}, '
                         f'size = {self.position.size}')

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(f'SELL EXECUTED, '
                         f'Price: {order.executed.price:.2f}, '
                         f'Cost: {order.executed.value:.2f}, '
                         f'Comm: {order.executed.comm:.2f}, '
                         f'size = {self.position.size}')

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log(f'OPERATION PROFIT, GROSS {trade.pnl:.2f}, '
                 f'NET {trade.pnlcomm:.2f}, '
                 f'size = {self.position.size}')