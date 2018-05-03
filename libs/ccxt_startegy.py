from libs.strategy import basicStrategy


class S(basicStrategy):
    
    def __init__(self):
        self.order = None
        self.dataclose = self.datas[0].close

    def next(self):
        self.log(self.dataclose[0], doprint=True)
        if self.order:
            return
