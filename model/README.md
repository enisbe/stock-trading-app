# Price Prediction Model

# Components

1. Training Files
2. Prediction Files
3. Strategy and backtest


# Portfolio Strategy Model

Portfolio strategy model uses predicted prices of stocks compositing S&P 500 as the base.
Below demonstrates how the model works:

1. After receiving the predicted prices from the forecast model, a collection of top 20 stocks with the highest expected return
are selected by the model to build up the portfolio. 

2. The trading strategy model then conduct portfolio optimization among the selected stocks and allocate the weight to each stock within the portfolio.

3. The objective of the optimization model is to maximizie the sharpe ratio of the portfolio and the sum of the weights of stocks are set to 1 as the constraint.

4. After the weights allocation is complete, the symbol of selected stocks along with the assigned weight is passed to the trading execution model for execution.

# Backtesting

In addition to weight allocation, our portfolio strategy model also provides a backtesting functinality. After the portfolio optimization is achieved, the backtesting
model will backtest the performance of optimized portfolio using historical data to assess the profitability of the strategy. Furthermore, the backtesting model
also provides a comparison between the performance of our opitimized portfolio and the performance of benchmark index -- S&P 500 to show if our strategy outperforms the
benchmark. The comparison is presented in two formats, one is the total asset amounts across the time period and the other is in the format of cumulative return. Visualization of the performance chart is also generated to increase the visibility of valuable insights.

Please see strategy and backtest model for further detail.
