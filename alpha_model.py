class MovingAverageAlphaModel(AlphaModel):
    ''' Alpha model: Price > SMA own asset, else own RiskOff (IEF). 
        AggressiveModel: EqualWeight top6 ranked by average 1,3,6,12month momentum, if Price > SMA. Else RiskOff.
    '''

    def __init__(self, smaLength=200, resolution=Resolution.Daily, predictionInterval=31):
        '''Initializes a new instance of the SmaAlphaModel class
        Args:
            period: The SMA period
            resolution: The reolution for the SMA'''
        self.smaLength = smaLength
        self.resolution = resolution
        self.predictionInterval = predictionInterval
        self.symbolDataBySymbol = {}
        self.month = -1

    def Update(self, algorithm, data):
        '''This is called each time the algorithm receives data for (@resolution of) subscribed securities
        Returns: The new insights generated.
        NOTE: analysis only occurs at month start, any generated signals intra-month are disregarded.'''
        if self.month == algorithm.Time.month:
            return []
        self.month = algorithm.Time.month
        

        insights = []
        riskOnWeight = 0    
        riskOffAsset = 'IEF'
        
        for symbol, symbolData in self.symbolDataBySymbol.items():

            price = algorithm.Securities[symbol].Price
            # Reset indicator, get fresh historical data, pump into indicator
            symbolData.MovingAverage.Reset()
            history = algorithm.History([symbol], self.smaLength, self.resolution)
            
            for time, row in history.loc[symbol].iterrows():
                symbolData.MovingAverage.Update(time, row["close"])
            
            # Own an asset if it is above its SMA, else allocate to IEF RiskOff Asset.
            if price != 0 and symbolData.MovingAverage.IsReady:

                if price > symbolData.MovingAverage.Current.Value:
                    insights.append( Insight.Price(symbol, timedelta(days=self.predictionInterval), InsightDirection.Up,  None, None, None, symbolData.Weight))
                    riskOnWeight += symbolData.Weight
                elif price < symbolData.MovingAverage.Current.Value:
                    insights.append( Insight.Price(symbol, timedelta(days=self.predictionInterval), InsightDirection.Flat,  None, None, None, 0) )
                    
        riskOffWeight = 1 - riskOnWeight   
        insights.append( Insight.Price(riskOffAsset, timedelta(days=self.predictionInterval), InsightDirection.Up,  None, None, None, riskOffWeight) )
        return insights


    def OnSecuritiesChanged(self, algorithm, changes):
        # As this is a static portfolio this will only be called ONCE.
        for added in changes.AddedSecurities:
            # Get historical data & check for existence in symbolData
            history = algorithm.History([added.Symbol], self.smaLength, self.resolution)
            symbolData = self.symbolDataBySymbol.get(added.Symbol)
            
            if symbolData is None:
                # Create an instance, initialise Indicator, pump in history
                symbolData = SymbolData(added)
                symbolData.MovingAverage = algorithm.SMA(added.Symbol, self.smaLength, self.resolution)
                for time, row in history.loc[added.Symbol].iterrows():
                    symbolData.MovingAverage.Update(time, row["close"])
                self.symbolDataBySymbol[added.Symbol] = symbolData
            else:
                # As this is a static portfolio this will never be called.
                symbolData.MovingAverage.Reset()
                for time, row in history.loc[added.Symbol].iterrows():
                    symbolData.MovingAverage.Update(time, row["close"])
                    
        # TODO: Needs to be amended for when securites are removed. Doesn't apply to static portfolio.           
      


class SymbolData:
    
    def __init__(self, security):
        self.Security = security
        self.Symbol = security.Symbol
        self.MovingAverage = None
        
        # This is messy. I'd like to avoid hard coding symbols here... not sure exactly how yet
        if str(self.Symbol) in ['VLUE', 'MTUM', 'VBR', 'XSMO', 'IEF', 'TLT', 'LQD', 'BWX']:
            self.Weight = 0.05 
            
        elif str(self.Symbol) in ['EFA', 'VWO', 'DBC', 'GLD']:
            self.Weight = 0.1 
        
        elif str(self.Symbol) == 'VNQ':
            self.Weight = 0.2 
        
        
"""        
5% US Large Value, (VLUE, 2013/05)
5% US Large Momentum (SPMO, 2015/9)
5% US Small Cap Value (VBR)
5% US Small Cap Momentum (XSMO) 

10% Foreign Developed (EFA)
10% Foreign Emerging (VWO)

5% US 10Y Gov Bonds (IEF)
5% US 30Y Gov Bonds (TLT)
5% US Corporate Bonds (LQD)
5% Foreign 10Y Gov Bonds (BWX)

10% Commodities (DBC)
10% Gold (GLD)
20% NAREIT (VNQ)
"""