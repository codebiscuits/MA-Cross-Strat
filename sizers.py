import backtrader as bt


class PercentSizer(bt.Sizer):
    '''This sizer return percents of available cash
    Params:
      - ``percents`` (default: ``20``)
    '''

    params = (
        ('percents', 25),
        ('retint', False),  # return an int size or rather the float value
    )

    def __init__(self):
        pass

    def _getsizing(self, comminfo, cash, data, isbuy):
        position = self.broker.getposition(data)
        if not position:
            size = cash / data.close[0] * (self.params.percents / 100)
        else:
            size = position.size

        if self.p.retint:
            size = int(size)

        return size