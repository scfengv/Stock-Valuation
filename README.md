# Discounted Cash Flow Model
Build: Feb 17, 2024

Revise: Oct 17, 2024
## Introduction

This five-year Discounted Cash Flow (DCF) model is designed to estimate the intrinsic value of publicly traded companies based on projected future cash flows. Leveraging financial data obtained through the `yfinance` API, this comprehensive valuation tool performs a series of complex calculations, including future **revenue** forecasts, **EBIT** (Earnings Before Interest and Taxes), **EBIAT** (Earnings Before Interest After Taxes), **Free Cash Flow**, **Weighted Average Cost of Capital** (WACC), and **Terminal Value**. The model's primary outputs are the **implied stock price** and the associated **margin of safety**, providing investors with crucial metrics for informed decision-making. Additionally, the model employs a **bisection algorithm** to compute the **implied revenue growth rate** that aligns the calculated stock price with the current market price, offering further insight into market expectations.

## Requirements
- Python 3.x

```python
pip install -r requirements.txt
```

## Usage
- Take **Coca-Cola (KO)** as an example

```bash
python DCFModel.py --ticker KO
```

Arguments:
- `--ticker`: Stock ticker symbol (Required)
- `--TGR`: Terminal Growth Rate (Default: `0.03`)
- `--riskfree`: Risk-free rate ticker symbol (Default: `"^TNX"`)
- `--market`: Market return ticker symbol (Default: `"VTI"`)

```bash
python DCFModel.py --ticker SYMBOL [--TGR RATE] [--riskfree SYMBOL] [--market SYMBOL]
python DCFModel.py --ticker NVDA    --TGR 0.02   --riskfree ^FVX     --market VT
```

## Result

```bash
Implied Stock Price: 76.18
Margin of Safety: 8.31%

Current price: 70.34 ; Implied Growth Rate: 2.87%
```

## Free Cash Flow

Free cash flow (FCF) represents the cash that a company generates after accounting for cash outflows to support its operations and maintain its capital assets. FCF is a measure of profitability that **excludes the non-cash expenses** of the income statement. It also includes **spending on equipment and assets**, as well as changes in working capital from the balance sheet.

```math
FCF =
EBIT*(1-Tax \%) + Depreciation\ \&\ Amortization - Capital\ Expenditures - Change\ in\ Net\ Working\ Capital
```

```math
Net\ Working\ Capital = Current\ Operating\ Asset - Current\ Operating\ Liability
```

```python
def _FreeCashFlow(self):
    return (self.EBIAT + self.FutureDA - self.FutureCapEx - self.FutureNWC)
```

## Discounted Cash Flow

Discounted cash flow (DCF) is a valuation method that estimates the value of an investment using its expected future cash flows to determine the **present value** (the value of an investment today).

### Calculating DCF

```math
DCF = \frac{CF_1}{(1+r)^1} + \frac{CF_2}{(1+r)^2} + ... + \frac{CF_n}{(1+r)^n}
```

1. Forecast the expected cash flow
2. Determine the discount rate
3. Discount the forecasted cash flow back to the present day

```python
def _DiscountedCashFlow(self):
    DiscountedCashFlow = sum(
        pd.Series((fcf / ((1 + self.WACC) ** (0.5 + i))) for i, fcf in enumerate(self.FutureFreeCashFlow))
    )
    DiscountedTerminalValue = self.TerminalValue / ((1 + self.WACC) ** 5)
    EnterpriseValue = DiscountedCashFlow + DiscountedTerminalValue
    return EnterpriseValue
```

## WACC

WACC (Weighted Average Cost of Capital) is company's average after-tax cost of capital, such as debt and equity. WACC is a common way to determine the required rate of return (RRR) and discount rate for future cash flow in DCF analysis.

WACC is calculated by multiplying the cost of each capital source (debt and equity) by its relevant weight and then adding those results together.

```math
WACC = W_D * R_D * (1-Tax \%) + W_E * R_E
```

- Weighted value of debt-based financing
```math
Weight\ of\ Debt\ (W_D) = \frac{Debt}{Debt\ +\ Market\ Cap}
```

```math
Cost\ of\ Debt\ (R_D) = \frac{Interest\ Expense}{Debt}
```

Cost of Debt is calculated by averaging the yield to maturity for a company's outstanding debts. Businesses are able to deduct interest expenses from their taxes. Because of this, the net cost of a company's debt is the amount of interest it is paying minus the amount of interest it can deduct on its taxes.

- Weighted value of equity-based financing
```math
Weight\ of\ Equity\ (W_E) = \frac{Market\ Cap}{Debt\ +\ Market\ Cap}
```

```math
Cost\ of\ Equity\ (R_E) = Risk-Free\ Rate\ +\ Beta * (Expected\ Market\ Return - Risk-Free\ Rate)
```

Cost of Equity is calculated by capital asset pricing model (CAPM), representing the expected return of investment. I use **VTI's 5y average return** as Expected Market Return ($15.29 \%$, 2024/10/17) and **U.S. 10 Year Treasury yield** as Risk-Free Rate ($4.032 \%$, 2024/10/17). Risk-Free Rate is the time value of money. The difference between Expected Market Return and Risk-Free Rate is market risk premium, which is the expected compensation for taking on additional risk.

Beta compares a stock's volatility or systematic risk to the market. A stock’s beta is then multiplied by the market risk premium, representing the RRR or discount rate.

```python
def _WACC(self):
    WeightofDebt = self.debt / (self.debt + self.MarketCap)
    WeightofEquity = self.MarketCap / (self.debt + self.MarketCap)
    CostofDebt = self.interest / self.debt
    CostofEquity = self.RiskFree + (self.beta * (self.MarketReturn - self.RiskFree))
    WACC = WeightofDebt * CostofDebt * (1 - self.TaxRate) + WeightofEquity * CostofEquity
    return WACC
```

## Terminal Value
[Wall Street Oasis | Terminal Value](https://www.wallstreetoasis.com/resources/skills/valuation/terminal-value)  
[Wall Street Oasis | EBIT vs EBITDA](https://www.wallstreetoasis.com/resources/skills/finance/exit-multiple)  
### Perpetual Growth Method
The perpetual growth method assumes that a company will **always produce cash flows at a steady rate** after the projection time.  
$$Terminal\ Value = \frac{Final\ Year\ FCF\ *\ (1\ +\ Perpetuity\ Growth\ Rate)}{(Discount\ Rate\ -\ Perpetuity\ Growth\ Rate)}$$

Advantages:
- Consist with the theory of discounted cash flow valuation.
- It is widely used and accepted by academics and practitioners.

Drawbacks:
- It is sensitive to the assumptions of the growth rate and the discount rate.
- Improbable in a dynamic and competitive market.
- This is because it ignores the potential changes in the industry structure.

```python
def _CalculateTerminalValue(self):
    return (self.FutureFreeCashFlow[4] * (1 + self.TerminalGrowthRate)) / (self.WACC - self.TerminalGrowthRate)
```

---
### Exit Multiple Method
The exit multiple method assumes that a company will **be sold after the forecast period** for a multiple of some market indicator.  

$$Terminal\ Value\ = Final\ Year\ Metric\ *\ Exit\ Multiple$$

Advantages:  
- Reflecting the market expectations and valuation multiples of comparable companies.
- Using market-based data rather than subjective assumptions about growth rates and margins.

Drawbacks:
- It is more difficult and subjective to find and select appropriate multiples and comparable companies.
- It is more uncertain and volatile, depending on market conditions and sentiments that may change over time or vary across different sectors.

#### EBITDA multiple
- **Mature & Stable** companies with consistent cash flows and margins
- It may NOT be suitable for **high-growth** or **low-margin** companies like technology or biotech.

#### EBIT multiple
- Include depreciation and amortization, which is particularly useful while analyzing **capital-intensive** businesses where depreciation is a true economic cost.
- Such as, automobile manufacturing, energy, steel production, and telecommunications.

#### Revenue multiple
- Often used for **high-growth** or **low-margin** companies with strong revenue potential but **not profitable** or have **negative cash flows**.
- It may NOT be suitable for companies with **stable revenue but declining growth**.

#### Earnings multiple
- Often used for profitable and growing companies with **positive cash flows and earnings**, such as **consumer discretionary**.

---




## Reference

- [Investopedia](https://www.investopedia.com)
- Stock relevant data: [Yahoo Finance](https://finance.yahoo.com)
- Enterprise Value Multiples by Sector: [NYU](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/vebitda.html)

## Disclaimer
- This tool is for educational and research purposes only. It should not be considered as financial advice. Always conduct your own research and consult with a qualified financial advisor before making investment decisions.
