'''An implementation of Meb Faber's base model: Global Tactical Asset Allocation model GTAA(13) 
with 10-month SimpleMovingAverage Filter (200day) and (monthly rebalance), as found in the paper: 
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461
"A Quantitative Approach to Tactical Asset Allocation" published May 2006.
Analysis only occurs at month End/Start, signals are NOT generated intra-month.
'''
# self.Debug(str(dir( x )))
from alpha_model import MovingAverageAlphaModel

class GlobalTacticalAssetAllocation(QCAlgorithm):
    
    def Initialize(self):
        
        #self.SetStartDate(date(2014, 1, 29) + timedelta(days=200)) 
        self.SetStartDate(2014, 5, 20)
        self.SetEndDate(2020, 5, 20)
        self.SetCash(100000) 
        self.Settings.FreePortfolioValuePercentage = 0.02
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.UniverseSettings.Resolution = Resolution.Daily
        symbols = [Symbol.Create(ticker, SecurityType.Equity, Market.USA) 
                for ticker in [ 'VLUE',     # 5% US Large Value, (VLUE, 2013/05)
                                'MTUM',     # 5% US Large Momentum (MTUM, 2013/5)
                                'VBR',      # 5% US Small Cap Value (VBR)
                                'XSMO',     # 5% US Small Cap Momentum (XSMO) 
                                'EFA',      # 10% Foreign Developed (EFA)
                                'VWO',      # 10% Foreign Emerging (VWO)
                                'IEF',      # 5% US 10Y Gov Bonds (IEF)
                                'TLT',      # 5% US 30Y Gov Bonds (TLT)
                                'LQD',      # 5% US Corporate Bonds (LQD)
                                'BWX',      # 5% Foreign 10Y Gov Bonds (BWX)
                                'DBC',      # 10% Commodities (DBC)
                                'GLD',      # 10% Gold (GLD)
                                'VNQ'       # 20% NAREIT (VNQ)
                                ]]
        self.AddUniverseSelection( ManualUniverseSelectionModel(symbols) )
        self.AddAlpha( ConstantAlphaModel(InsightType.Price, InsightDirection.Up, timedelta(days=31)) )
        #self.AddAlpha( MovingAverageAlphaModel() )
        self.Settings.RebalancePortfolioOnInsightChanges = False   
        self.Settings.RebalancePortfolioOnSecurityChanges = False  
        self.SetPortfolioConstruction( EqualWeightingPortfolioConstructionModel(self.DateRules.MonthStart('IEF')) )
        #self.SetPortfolioConstruction( InsightWeightingPortfolioConstructionModel(self.DateRules.MonthStart('IEF'), PortfolioBias.Long) )

        self.SetExecution( ImmediateExecutionModel() ) 
        
        self.AddRiskManagement( NullRiskManagementModel() )
        
        
"""
OR, Aggressive version: Select top6 ranked by average 1,3,6,12month momentum.
        # ETF Symbol/Weighting Tuple's
        self.etfs = [   # (1x) ETF EarliestStartDate: 2014/02
                        (self.AddEquity('VLUE', Resolution.Daily).Symbol, 0.05),    # 5% US Large Value, (VLUE, 2013/05)
                        (self.AddEquity('MTUM', Resolution.Daily).Symbol, 0.05),    # 5% US Large Momentum (MTUM, 2013/5)
                        (self.AddEquity('VBR', Resolution.Daily).Symbol, 0.05),     # 5% US Small Cap Value (VBR)
                        (self.AddEquity('XSMO', Resolution.Daily).Symbol, 0.05),    # 5% US Small Cap Momentum (XSMO) 
                        (self.AddEquity('EFA', Resolution.Daily).Symbol, 0.1),      # 10% Foreign Developed (EFA)
                        (self.AddEquity('VWO', Resolution.Daily).Symbol, 0.1),      # 10% Foreign Emerging (VWO) 
                        (self.AddEquity('IEF', Resolution.Daily).Symbol, 0.05),     # 5% US 10Y Gov Bonds (IEF)
                        (self.AddEquity('TLT', Resolution.Daily).Symbol, 0.05),     # 5% US 30Y Gov Bonds (TLT)
                        (self.AddEquity('LQD', Resolution.Daily).Symbol, 0.05),     # 5% US Corporate Bonds (LQD)
                        (self.AddEquity('BWX', Resolution.Daily).Symbol, 0.05),     # 5% Foreign 10Y Gov Bonds (BWX)
                        (self.AddEquity('DBC', Resolution.Daily).Symbol, 0.1),      # 10% Commodities (DBC)
                        (self.AddEquity('VWO', Resolution.Daily).Symbol, 0.1),      # 10% Foreign Emerging (VWO)      
                        (self.AddEquity('GLD', Resolution.Daily).Symbol, 0.1),      # 10% Gold (GLD)
                        (self.AddEquity('VNQ', Resolution.Daily).Symbol, 0.2)      # 20% NAREIT (VNQ)
    
                    ]

"""