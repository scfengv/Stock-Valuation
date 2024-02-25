# Stock-Valuation

## Introduction
This project serves as a 5-year DCF model to evaluate companies' target prices, using Selenium to fetch stock information mainly from [Yahoo Finance](https://finance.yahoo.com) & [Stock Analysis](https://stockanalysis.com). The information includes everything needed to calculate DCF. Start by calculating WACC; after that, three common methods are used, perpetual growth / EV2EBIT multiple / EV2EBITDA multiple, to determine the terminal value depending on the industry of the company. Instead of discounting Free Cash Flow at the end of the year, as most people do, I reference [Ben's way](https://www.youtube.com/@rareliquid), setting the discount period in the middle of the year (*Mid-year convention*, assuming getting the cash flow in the middle of the year instead of at the end of the year). In the end, I tried to solve a quintic equation to work out the market's expected five-year average growth rate as implied by current stock prices.

- Take **Broadcom Inc. (AVGO)** as an example, which is a company I would like to buy recently.

## WACC
$WACC\ (Weighted\ Average\ Cost\ of\ Capital) = W_D * R_D * (1-tax\ rate) + W_E * R_E$ <br><br>
Weight of Debt ($W_D$) = $\Large\frac{Debt}{Debt\ +\ Market\ Cap}$ <br><br>
Weight of Equity ($W_E$) = $\Large\frac{Market\ Cap}{Debt\ +\ Market\ Cap}$ <br><br>
Cost of Debt ($R_D$) = $\Large\frac{Interest\ Expense}{Debt}$ <br><br>
Cost of Equity ($R_E$) = $Treasury\ Bond\ Rate\ +\ Beta * (Expected\ Market\ Return - Treasury\ Bond\ Rate\ )$

* Expected Market Return: VTI 10-Year Trailing Returns
* Treasury Bond Rate: 10-Year Treasury Rate

---
#### Ex: AVGO

Expected Market Return: $11.91 \\%$  
The value of 10-year Treasury Bond Yield: $4.26 \\%$  
Market Premium: $7.65 \\%$  


Weight of Debt = $6.0715 \\%$  
Weight of Equity = $93.9285 \\%$  
Cost of Debt = $4.1347 \\%$  
Cost of Euqity = $13.9296 \\%$  
**WACC** = $6.0715 \\% * 4.1347 \\% * (1 - 6.72\\%) + 93.9285 \\% * 13.9296 \\% = 13.318 \\%$

## Terminal Value
[Wall Street Oasis | Terminal Value](https://www.wallstreetoasis.com/resources/skills/valuation/terminal-value)  
[Wall Street Oasis | EBIT vs EBITDA](https://www.wallstreetoasis.com/resources/skills/finance/exit-multiple)  

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

---
#### Ex: AVGO
TTM Revenue: $35,819,000,000$

EBIT: $16,719,000,000$  
EBIT margin: $46.68 \\%$  
Average Industrial EV / EBIT of Semiconductor: $53.32$  
EV / EBIT of AVGO: $37.8$  
Terminal Value by EBIT multiple: $631,978,200,000$

EBITDA: $20,554,000,000$  
EBITDA margin: $57.38 \\%$  
Average Industrial EV / EBITDA of Semiconductor: $31.59$  
EV / EBITDA of AVGO: $30.74$  
Terminal Value by EBITDA multiple: $631,829,960,000$  

Terminal Value by Perpetual Growth Method: $339,856,060,388$

Latest 2023 Free Cash Flow:          $17,633,000,000$  
Free Cash Flow margin: $49.23 \\%$

Predicted 2024 Discounted Cash Flow: $19,276,168,806$    
Predicted 2025 Discounted Cash Flow: $19,795,465,950$  
Predicted 2026 Discounted Cash Flow: $20,134,707,875$  
Predicted 2027 Discounted Cash Flow: $20,479,763,509$  
Predicted 2028 Discounted Cash Flow: $20,830,732,484$  
Predicted Terminal value of Discounted Cash Flow:  $366,931,902,969$  

Net Present Value of AVGO: $467,448,741,593$

### Result
Target Price: $945.03$  
Current Price: $1296.37$  
Margin of Safety: $-27.1 \\%$  
Implied 5-year Growth Rate by current price: $57.7978 \\%$

```
g = (price * share_num - dcf_terminal + debt_num - ccs_num) / fcf_num
x = symbols('x')
quintic_equation = x**5 + x**4 + x**3 + x**2 + x - g
solutions = solve(quintic_equation, x)
numerical_solutions = [sol.evalf() for sol in solutions]
t = float(numerical_solutions[0])
r = t * (1 + wacc / 100) - 1
```


## Source of Data
- Stock relevant data: [Yahoo Finance](https://finance.yahoo.com), [Stock Analysis](https://stockanalysis.com)
- 10-Year Treasury Bond Rate: [YCharts](https://ycharts.com/indicators/10_year_treasury_rate)
- Enterprise Value Multiples by Sector: [NYU](https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/vebitda.html)

## Drawbacks
- Yet not able to calculate the growth rates of different businesses separately
