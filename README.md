# ASTrA - Automated Stock Trading App

**Authors**

June 2022

- Enis Becirbegovic - EnisBecirbegovic2022@u.northwestern.edu
- Mark Stockwell - MarkStockwell2021@u.northwestern.edu
- Oliver Zarate - OliverZarate2021@u.northwestern.edu
- Siying Zhang - SiyingZhang2022@u.northwestern.edu


# Table of Contents

|             |             |             |             |
| ----------- | ----------- | ----------- | ----------- |
| 1. [Summary](#summary)         | 4. [Components](#components) | 7. [Portfolio Strategy Model](#portfolio)   |  10. [Monitoring and Front-End](#monitoring)  | 
| 2. [Objective](#objective)     | 5. [Data Acquisition](#data_acquisition)   |  8. [Backtesting Model](#backtesting) |  11. [Installation and Usage](#installation) | 
| 3. [Overview](#overview)        | 6. [Model and Weighting](#model)         |  9. [Rebalance and Execution ](#rebalance) | |


**Summary** <a name="summary"></a>

This application was developed as part of [Northwestern Data Science](https://sps.northwestern.edu/masters/data-science/curriculum-specializations.php) Master of Science in Data Science program as one of the requirements for the
[Capstone](https://sps.northwestern.edu/masters/data-science/thesis-capstone.php) group project for the Data Engineering Specialization.

[#northwestern](https://www.linkedin.com/search/results/all/?keywords=%23northwestern) 
[#dataengineering](https://www.linkedin.com/search/results/all/?keywords=%23dataengineering%20northwestern%20university) 
[#capstone](https://www.linkedin.com/search/results/all/?keywords=%23capstone%20northwestern%20university)

**Objective** <a name="objective"></a>

To develop an end-to-end automated trading system that uses a time series model to make predictions for S&P stocks for the next market trading hour. The stock purchase / sell decisions are represented by a recommended portfolio weighting. A seperate service automates the portfolio rebalancing process and execute the trades in paper trading account. The fully automated application is deployed in google cloud. 

## Overview <a name="overview"></a>
------

<img src="./images/overview.png" alt="Application Overview"> 
ASTrA is a near real-time (~5 min latency) stock trading application that uses an NBeats (Neural basis expansion analysis for interpretable time series forecasting) deep learning machine learning algorithm to predict stock prices based on previous n periods. Stock predictions are fed into a portfolio optimization algorithm that uses Sharpe Ratios to minimize risk and maximize return. The process is as follows:

1. Google Cloud Scheduler is used to call a Cloud Run http endpoint every 5 minutes. The Cloud Run application takes a list of S&P 500 ticker symbols and retrieves the last 30 days of price history at 5 min intervals. This data is upserted to a SQL database (Azure).
2. Once the latest prices are available, the prediction model is called to calculate the expected price of each security over the next time period.
3. The predictions are passed to a second model which calculates the top 20 stocks to acquire and percent allocation for next time period.
4. A portfolio allocation file is uploaded to Google Cloud Storage, which triggers the trading execution Cloud Function. This function buys/sells securities as needed to achieve the desired allocation. Activity including details transaction history is written to the database for analysis. Upon completion of rebalance process an account summary with portfolio balance is also written.

  
## Components <a name="components"></a>

To enable portfolio recommendations, stock data is collected on the S&P 500 every 5 minutes. The data are used to make stock predictions for the upcoming hour (in 5-minute increments). The prediction data are combined with volatility data to find an optimally  weighted portfolio. The optimization is based on a sharpe ratio which finds the best expected return for given level of risk.

- **Data Architecture** - An [Azure relational database](./data/CreateAzureDB.ps1) was selected as main data storage layer to 1) handle high concurrency and transactional volume of inserts/deletes and 2) demonstrate the viability of hybrid/multi-vendor solutions.  The database has a 
[price_history table](./data/price_history_ddl.sql) that stores 500 stock ticker prices at 5 minute granularity for each trading day. A cloud run application ([main.py](./data/main.py)) calls the Yahoo finance API via the [yfinance package](https://pypi.org/project/yfinance/) to collect data and load the database. Cloud Run Scheduler is used to run the job every 5 minutes by calling the http endpoint with a list of tickers as parameters, e.g. https://yahoosp500etl-123456789.a.run.app/load_price_history?ticker=OXY|PARA|PAYC|PAYX.

- **Model Training** -  There were multiple models used for training. All were based on N-BEATS architecture (https://arxiv.org/abs/1905.10437). The two main models trained were daily stock data and 5 minute stock data. The later was used for production. Models were trained using google colab + GPUs. Training required data historical S&P data. Specifically price data for given intervals. 
- **Predictions** - Once the production model was trained. It was deployed to a google cloud cloud storage. In production, the model is accessed and loaded. Input to the model is collected from end points generated by the database. 
- **Target Portfolio Allocation** -  Logic is included to generate an optimal portfolio using by solving for the maximum sharp ratio. For more detail on Model Training, Predictions, and target allocation setting see sections below or (https://github.com/enisbe/stock-trading-app/blob/main/model/README.md)
- **Trade Execution** - Once the forecast is generated the rebalance and execution is executed in event-driven fashion. The process consist of file drop into a GCP bucket. The bucket listen to events and executes rebalance Cloud Function as well as the execution via Alpaca API. 

### Data Acquisition <a name="data_acquisition"></a>

<img src="./images/ETL.png" alt="Data pipelines"> 

Data Acquisition ETL Workflow

1. A Cloud Run application written in Python/Flask uses the yfinance python package to extract price history for all 500 S&P stocks.
2. Price history is written to an Azure database using Microsoft ODBC drivers and pyodbc package. The process loads a temp table with a large amount of data, then loads the main table with any rows that are in the temp table but not the main table. In most cases only the last 5 minutes of data will inserted into the main table. This process is idempotent and fault tolerant, it allows reruns of jobs on failure or to catch up on previous day.
3. The Cloud Run application has a /dump_table function that simplifies data distribution to the prediction model, essentially an http data source.
4. A Cloud Scheduler job is called with a list of tickers to collect data. 10 jobs are configured to run simultaneously with 50 tickers each, completing in about 1 minute.

### Model and Weighting <a name="model"></a>

<img src="./images/cloud-run-predict&weight.png" alt="Pulling Model, predicting, and providing allocation recommendations"> 

### Portfolio Strategy Model <a name="portfolio"></a>

Portfolio strategy model uses predicted prices of stocks compositing S&P 500 as the base. Detailed instruction is saved in the model folder.

The model output would be a basket of selected stocks along with the weight of each selected stock as shown in below chart.

<img src="./images/weights.png" alt="Portfolio Allocation">

### Backtesting Model <a name="backtesting"></a>

Within the Portfolio opitmization model, backtesting of opitmized portfolio is conducted using historical data. The backtesting model assesses the profitability of the optimized portfolio strategy and provides a comparison between the performance of opitimized portfolio and the performance of benchmark index -- SPY. Below chart displays the result of portfolio backtesting in cumulative return term.

<img src="./images/backtest.png" alt="Backtesting of Portfolio">


### Rebalance and Execution <a name="rebalance"></a>

Rebalance and execution is even-driven and function as a microservices application. Any file dropped in a target google cloud storage bucket (as long formatted and named correctly) will trigger rebalancing and execution process. This process is built and deployed as a cloud function. How to deploy the function can be found in [cf_rebalance folder](https://github.com/enisbe/stock-trading-app/tree/main/cf_rebalance). The process architecture is shown below.

<img src="./images/rebalance-process.png" alt="Rebalance Process"> 


### Monitoring and Front-End <a name="monitoring"></a>

Monitoring is a service designed to track account performance. Monitoring collects the information from the broker and saves it to the database. It is deployed as a cloud-run container and with a flask front end. The deployment link is found in [cf-monitor folder](https://github.com/enisbe/stock-trading-app/tree/main/cf_monitor).

<img src="./images/monitor-frontend.png" alt="Front end GUI"> 

Front-end is a service deployed as a [streamlit application](https://github.com/enisbe/stock-trading-app/tree/main/front_end). It connects to the database and calculates and displays the account performance.

<img src="./images/front-end.png" alt="Front end GUI"> 

## Installation and Usage <a name="installation"></a>

* Create local copy 
* Recommend using virutal env 
* run `make all` before commiting

