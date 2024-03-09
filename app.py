import pandas as pd
import psycopg2
import streamlit as st
import plotly.graph_objects as go
import numpy as np
# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="invstodb",
    user="admin",
    password="adminadmin"
)

query = "SELECT * FROM ticker_data ORDER BY datetime"
data = pd.read_sql_query(query, conn)

conn.close()

data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime')

# Implement trading strategies
def sma_crossover(data, short_window, long_window):
    data['SMA_Short'] = data['close'].rolling(window=short_window).mean()
    data['SMA_Long'] = data['close'].rolling(window=long_window).mean()
    data['Signal'] = 0.0
    data['Signal'][short_window:] = np.where(data['SMA_Short'][short_window:] > data['SMA_Long'][short_window:], 1.0, -1.0)
    return data

def rsi_strategy(data, window=14, overbought=70, oversold=30):
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss
    data['RSI'] = 100 - (100 / (1 + rs))
    data['Signal'] = 0.0
    data['Signal'][window:] = np.where((data['RSI'][window:] > overbought), -1.0, np.where((data['RSI'][window:] < oversold), 1.0, 0.0))
    return data

def macd_strategy(data, fast=12, slow=26, signal=9):
    data['EMA_Fast'] = data['close'].ewm(span=fast, adjust=False).mean()
    data['EMA_Slow'] = data['close'].ewm(span=slow, adjust=False).mean()
    data['MACD'] = data['EMA_Fast'] - data['EMA_Slow']
    data['Signal'] = data['MACD'].ewm(span=signal, adjust=False).mean()
    data['Signal'] = np.where(data['MACD'] > data['Signal'], 1.0, np.where(data['MACD'] < data['Signal'], -1.0, 0.0))
    return data



# Streamlit app
st.title("Trading Strategies")

start_date = st.sidebar.date_input("Start Date", data.index.min())
end_date = st.sidebar.date_input("End Date", data.index.max())
strategy = st.sidebar.selectbox("Select Strategy", ["SMA Crossover", "RSI", "MACD"])

# Filter data based on date range
filtered_data = data.loc[start_date:end_date]

# Implement selected strategy for Streamlit Operations
if strategy == "SMA Crossover":
    filtered_data = sma_crossover(filtered_data, 20, 50)
elif strategy == "RSI":
    filtered_data = rsi_strategy(filtered_data)
elif strategy == "MACD":
    filtered_data = macd_strategy(filtered_data)

filtered_data['Returns'] = np.log(filtered_data['close'] / filtered_data['close'].shift(1))
filtered_data['Strategy_Returns'] = filtered_data['Returns'] * filtered_data['Signal'].shift(1)
filtered_data['Cumulative_Returns'] = filtered_data['Strategy_Returns'].cumsum().apply(np.exp)

# Plot candlestick chart
fig = go.Figure(data=[go.Candlestick(
    x=filtered_data.index,
    open=filtered_data['open'],
    high=filtered_data['high'],
    low=filtered_data['low'],
    close=filtered_data['close']
)])

if strategy == "SMA Crossover":
    fig.add_trace(go.Scatter(
        x=filtered_data.index,
        y=filtered_data['SMA_Short'],
        mode='lines',
        name='SMA_Short'
    ))

    fig.add_trace(go.Scatter(
        x=filtered_data.index,
        y=filtered_data['SMA_Long'],
        mode='lines',
        name='SMA_Long'
    ))
elif strategy == "RSI":
    fig.add_trace(go.Scatter(
        x=filtered_data.index,
        y=filtered_data['RSI'],
        mode='lines',
        name='RSI'
    ))
elif strategy == "MACD":
    fig.add_trace(go.Scatter(
        x=filtered_data.index,
        y=filtered_data['MACD'],
        mode='lines',
        name='MACD'
    ))

    fig.add_trace(go.Scatter(
        x=filtered_data.index,
        y=filtered_data['Signal'],
        mode='lines',
        name='Signal'
    ))

fig.update_layout(
    title=f'{strategy} Strategy',
    xaxis_rangeslider_visible=False
)

st.plotly_chart(fig, use_container_width=True)

# Strategy performance
st.subheader("Strategy Performance")
st.write(f"Cumulative Returns: {filtered_data['Cumulative_Returns'].iloc[-1]:.2f}")