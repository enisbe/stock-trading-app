# Stock Trading App

* Create local copy 
* Recommend using virutal env 
* run `make all` before commiting


# Automated stock trading
----

**Summary**

This application was developed as part of Northwestern data science capston group project. 

**Objective** 

>  developed an automated trading system that relies on the a time series model to make decision when to buy/sell/hold stocks. Automate the rebalancing process and execute the trades in paper trading account. Deploy fully automated application in google cloud. 


  
## Components
------

TODO

## Data
-----
TODO

## Model and Weighting

-----<img src="./images/cloud-run-predict&weight.png" alt="Pulling Model, predicting, and providing allocation recommendations"> 

### Portfolio Strategy Model

Portfolio strategy model uses predicted prices of stocks compositing S&P 500 as the base. Detailed instruction is saved in the model folder.

The model output would be a basket of selected stocks along with the weight of each selected stock as shown in below chart.

<img src="./images/weights.png" alt="Portfolio Allocation">

### Backtesting Model

Within the Portfolio opitmization model, backtesting of opitmized portfolio is conducted using historical data. The backtesting model assesses the profitability of the optimized portfolio strategy and provides a comparison between the performance of opitimized portfolio and the performance of benchmark index -- SPY. Below chart displays the result of backtesting in cumulative return term.

<img src="./images/backtest.png" alt="Backtesting of Portfolio">


Rebalance and Monitoring
-----

TODO

<img src="./images/rebalance-process.png" alt="Front end GUI"> 
