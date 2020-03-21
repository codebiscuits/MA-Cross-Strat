import backtrader as bt


class PercentSizer(bt.Sizer):
    '''This sizer return percents of available cash
    Params:
      - ``percents`` (default: ``20``)
    '''

    params = (
        ('percents', 99),
        ('retint', False),  # return an int size or rather the float value
    )

    def __init__(self):
        pass

    def _getsizing(self, comminfo, cash, data, isbuy):
        size = cash / data.close[0] * (self.params.percents / 100)

        if self.p.retint:
            size = int(size)

        return size

class FixedSize(bt.Sizer):
    params = (('stake', 1),)

    def _getsizing(self, comminfo, cash, data, isbuy):
        return self.params.stake

class FixedReverser(bt.Sizer):

    params = (('stake', 1),)

    def __init__(self):
        pass

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        size = self.p.stake * (1 + (position.size != 0))
        return size