import numpy as np
import pandas as pd
import yfinance as yf
import warnings
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--ticker", dest = "ticker", default = None)
parser.add_argument("--TGR", dest = "TerminalGrowthRate", default = 0.03)
parser.add_argument("--riskfree", dest = "RiskFree", default = "^TNX")
parser.add_argument("--market", dest = "MarketReturn", default = "VTI")
args = parser.parse_args()

class DCFModel():
    def __init__(self, ticker, args):
        self.ticker = ticker
        self.stock = yf.Ticker(f"{ticker}")
        self.income = self.stock.income_stmt
        self.balance = self.stock.balance_sheet
        self.cashflow = self.stock.cash_flow
        self.EBIT = None
        self.revenue = None
        self.TaxRate = None
        self.TerminalGrowthRate = args.TerminalGrowthRate
        self.weights = np.array([0.4, 0.3, 0.2, 0.1])
        self.tax_weights = np.array([0.5, 0.3, 0.2])
        self.MarketCap = self.stock.info["marketCap"]
        self.debt = self.stock.info["totalDebt"]
        self.cash = self.stock.info["totalCash"]
        self.shares = self.stock.info["sharesOutstanding"]
        self.beta = self.stock.info["beta"]
        self.interest = self.income.loc["Interest Expense"][0]
        self.RiskFree = yf.Ticker(f"{args.RiskFree}").info["previousClose"] / 100
        self.MarketReturn = yf.Ticker(f"{args.MarketReturn}").info["threeYearAverageReturn"]
        self.price = self.stock.info["previousClose"]
        self.FutureRevenue = self._CalculateFutureRevenue()
        self.FutureEBIT = self._CalculateFutureEBIT()
        self.FutureTax = self._CalculateFutureTax()
        self.EBIAT = self._CalculateEBIAT()
        self.FutureDA = self._CalculateFutureDepreciationAmortization()
        self.FutureCapEx = self._CalculateFutureCapEx()
        self.FutureNWC = self._CalculateFutureNWC()
        self.FutureFreeCashFlow = self._FreeCashFlow()
        self.WACC = self._WACC()
        self.TerminalValue = self._CalculateTerminalValue()
        self.EnterpriseValue = self._DiscountedCashFlow()
        self.ImpliedSharePrice = self._CalculateImpliedSharePrice()
        self.MarginofSafety = ((self.ImpliedSharePrice - self.price) / self.price)

    def _CalculateFutureRevenue(self):
        self.revenue = self.income.loc["Total Revenue"][:-1]
        Rev_TTM = self.stock.revenue_estimate.loc["0y", "avg"]
        Rev_growth = 1 + self.stock.revenue_estimate.loc["+1y", "growth"]
        FutureRevenue = pd.Series(Rev_TTM * (Rev_growth ** i) for i in range(5))
        return FutureRevenue
    
    def _CalculateFutureEBIT(self):
        self.EBIT = self.income.loc["EBIT"][:-1]
        EBIT_margin = np.average(self.EBIT / self.revenue, weights = self.weights)
        FutureEBIT = self.FutureRevenue * EBIT_margin
        return FutureEBIT
    
    def _CalculateFutureTax(self):
        Tax = self.income.loc["Tax Provision"][:-1]
        self.TaxRate = np.average((Tax / self.EBIT)[:3], weights = self.tax_weights)
        FutureTax = self.FutureEBIT * self.TaxRate
        return FutureTax
    
    def _CalculateEBIAT(self):
        return (self.FutureEBIT - self.FutureTax)
    
    def _CalculateFutureDepreciationAmortization(self):
        DA = abs(self.cashflow.loc["Depreciation And Amortization"][:-1])
        DA_margin = np.average(DA / self.revenue, weights = self.weights)
        FutureDA = self.FutureRevenue * DA_margin
        return FutureDA
    
    def _CalculateFutureCapEx(self):
        CapEx = abs(self.cashflow.loc["Capital Expenditure"][:-1])
        CapEx_margin = np.average(CapEx / self.revenue, weights = self.weights)
        FutureCapEx = self.FutureRevenue * CapEx_margin
        return FutureCapEx
    
    def _CalculateFutureNWC(self):
        NWC = self.cashflow.loc["Change In Working Capital"][:-1]
        NWC_margin = np.average(NWC / self.revenue, weights = self.weights)
        FutureNWC = self.FutureRevenue * NWC_margin
        return FutureNWC
    
    def _FreeCashFlow(self):
        return (self.EBIAT + self.FutureDA - self.FutureCapEx - self.FutureNWC)
    
    def _WACC(self):
        WeightofDebt = self.debt / (self.debt + self.MarketCap)
        WeightofEquity = self.MarketCap / (self.debt + self.MarketCap)
        CostofDebt = self.interest / self.debt
        CostofEquity = self.RiskFree + (self.beta * (self.MarketReturn - self.RiskFree))
        WACC = WeightofDebt * CostofDebt * (1 - self.TaxRate) + WeightofEquity * CostofEquity
        return WACC
    
    def _CalculateTerminalValue(self):
        return (self.FutureFreeCashFlow[4] * (1 + self.TerminalGrowthRate)) / (self.WACC - self.TerminalGrowthRate)
    
    def _DiscountedCashFlow(self):
        DiscountedCashFlow = sum(
            pd.Series((fcf / ((1 + self.WACC) ** (0.5 + i))) for i, fcf in enumerate(self.FutureFreeCashFlow))
        )
        DiscountedTerminalValue = self.TerminalValue / ((1 + self.WACC) ** 5)
        EnterpriseValue = DiscountedCashFlow + DiscountedTerminalValue
        return EnterpriseValue
    
    def _CalculateImpliedSharePrice(self):
        EquityValue = self.EnterpriseValue - self.debt + self.cash
        ImpliedSharePrice = EquityValue / self.shares
        return ImpliedSharePrice

    def CalculateImpliedGrowthRate(self, tolerance = 0.01, max_iterations = 100):
        def calculate_price(growth_rate):
            self.FutureRevenue = pd.Series(self.revenue.iloc[0] * ((1 + growth_rate) ** i) for i in range(5))
            self.FutureEBIT = self._CalculateFutureEBIT()
            self.FutureTax = self._CalculateFutureTax()
            self.EBIAT = self._CalculateEBIAT()
            self.FutureDA = self._CalculateFutureDepreciationAmortization()
            self.FutureCapEx = self._CalculateFutureCapEx()
            self.FutureNWC = self._CalculateFutureNWC()
            self.FutureFreeCashFlow = self._FreeCashFlow()
            self.TerminalValue = self._CalculateTerminalValue()
            self.EnterpriseValue = self._DiscountedCashFlow()
            return self._CalculateImpliedSharePrice()

        lower = -0.5
        upper = 0.5
        
        for _ in range(max_iterations):
            mid = (lower + upper) / 2
            calculated_price = calculate_price(mid)
            
            if abs(calculated_price - self.price) < tolerance:
                return mid
            
            if calculated_price > self.price:
                upper = mid
            else:
                lower = mid
        
        raise ValueError("Implied growth rate calculation did not converge")
    

def main():
    warnings.filterwarnings("ignore")
    ticker = str(f"{args.ticker}").upper()
    model = DCFModel(ticker, args)
    print(f"Implied Stock Price: {model.ImpliedSharePrice:.2f}")
    print(f"Margin of Safety: {model.MarginofSafety:.2%}")

    ImpliedGrowthRate = model.CalculateImpliedGrowthRate()
    print(f"Current price: {model.price} ; Implied Growth Rate: {ImpliedGrowthRate:.2%}")

if __name__ == "__main__":
    main()