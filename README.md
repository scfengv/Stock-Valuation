# Stock-Valuation

## Introduction
This project serves as a 5-year DCF model to evaluate companies' target prices, using Selenium to fetch stock information mainly from [Yahoo Finance](https://finance.yahoo.com) & [Stock Analysis](https://stockanalysis.com). The information includes everything needed to calculate DCF. Start by calculating WACC; after that, three common methods are used, perpetual growth / EV2EBIT multiple / EV2EBITDA multiple, to determine the terminal value depending on the industry of the company. Instead of discounting Free Cash Flow at the end of the year, as most people do, I reference [Ben's way](https://www.youtube.com/@rareliquid), setting the discount period in the middle of the year (*Mid-year convention*, assuming getting the cash flow in the middle of the year instead of at the end of the year). In the end, I tried to solve a quintic equation to work out the market's expected five-year average growth rate as implied by current stock prices.

## WACC
$WACC\ (Weighted\ Average\ Cost\ of\ Capital) = W_D * R_D * (1-tax\ rate) + W_E * R_E$ <br><br>
Weight of Debt ($W_D$) = $\Large\frac{Debt}{Debt\ +\ Market\ Cap}$ <br><br>
Weight of Equity ($W_E$) = $\Large\frac{Market\ Cap}{Debt\ +\ Market\ Cap}$ <br><br>
Cost of Debt ($R_D$) = $\Large\frac{Interest\ Expense}{Debt}$ <br><br>
Cost of Equity ($R_E$) = $Treasury\ Bond\ Rate\ +\ Beta * (Expected\ Market\ Return - Treasury\ Bond\ Rate\ )$

* Expected Market Return: VTI 10-Year Trailing Returns
* Treasury Bond Rate: 10-Year Treasury Rate
