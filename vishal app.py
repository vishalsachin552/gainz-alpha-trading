import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ta
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Gainz Alpha V2",
    page_icon="📈",
    layout="wide"
)

st.title("🚀 Gainz Alpha V2 - Trading Tool")

# Sectors data
SECTORS = {
    'Technology': ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'META', 'TSLA'],
    'Healthcare': ['JNJ', 'UNH', 'LLY', 'PFE', 'ABBV'],
    'Financial': ['BRK-B', 'JPM', 'V', 'MA', 'BAC']
}

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol, period='1d', interval='5m'):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period=period, interval=interval)
        info = stock.info
        return {
            'data': data,
            'info': info,
            'sector': info.get('sector', 'Unknown'),
            'volume': info.get('volume', 0)
        }
    except:
        return None

def calculate_indicators(data):
    df = data.copy()
    df['EMA_9'] = ta.trend.ema_indicator(df['Close'], window=9)
    df['EMA_21'] = ta.trend.ema_indicator(df['Close'], window=21)
    df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
    df['MACD'] = ta.trend.macd(df['Close'])
    df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
    return df

def get_signal(df):
    last_row = df.iloc[-1]
    
    # Simple strategy
    if (last_row['EMA_9'] > last_row['EMA_21']) and (last_row['RSI'] < 70):
        return "🟢 BUY"
    elif (last_row['EMA_9'] < last_row['EMA_21']) and (last_row['RSI'] > 30):
        return "🔴 SELL"
    else:
        return "⚪ HOLD"

# Sidebar
st.sidebar.title("🎯 Navigation")
option = st.sidebar.selectbox("Choose:", ["Stock Analyzer", "Watchlist"])

if option == "Stock Analyzer":
    st.header("📊 Stock Analyzer")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        symbol = st.text_input("Enter Stock Symbol:", value="AAPL").upper()
    with col2:
        if st.button("Analyze"):
            # Get data
            stock_data = get_stock_data(symbol)
            
            if stock_data:
                # Calculate indicators
                df = calculate_indicators(stock_data['data'])
                signal = get_signal(df)
                
                # Display metrics
                current_price = df['Close'].iloc[-1]
                day_change = ((current_price - df['Open'].iloc[0]) / df['Open'].iloc[0]) * 100
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Price", f"${current_price:.2f}")
                with col2:
                    st.metric("Day Change", f"{day_change:.2f}%")
                with col3:
                    st.metric("Signal", signal)
                
                # Simple chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price'))
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_9'], name='EMA 9'))
                fig.add_trace(go.Scatter(x=df.index, y=df['EMA_21'], name='EMA 21'))
                
                fig.update_layout(title=f"{symbol} - Price Chart", height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                # Technical details
                with st.expander("📈 Technical Details"):
                    last = df.iloc[-1]
                    st.write(f"**RSI:** {last['RSI']:.1f}")
                    st.write(f"**EMA 9:** ${last['EMA_9']:.2f}")
                    st.write(f"**EMA 21:** ${last['EMA_21']:.2f}")
                    st.write(f"**Volume:** {stock_data['volume']:,}")

else:  # Watchlist
    st.header("⭐ Watchlist")
    
    # Default watchlist
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = ['AAPL', 'MSFT', 'GOOGL', 'NVDA', 'TSLA']
    
    # Add symbol
    new_symbol = st.text_input("Add Symbol:").upper()
    if st.button("Add to Watchlist") and new_symbol:
        if new_symbol not in st.session_state.watchlist:
            st.session_state.watchlist.append(new_symbol)
    
    # Display watchlist
    watchlist_data = []
    for symbol in st.session_state.watchlist:
        stock_data = get_stock_data(symbol)
        if stock_data:
            df = calculate_indicators(stock_data['data'])
            signal = get_signal(df)
            current_price = df['Close'].iloc[-1]
            
            watchlist_data.append({
                'Symbol': symbol,
                'Price': f"${current_price:.2f}",
                'Signal': signal,
                'RSI': f"{df['RSI'].iloc[-1]:.1f}"
            })
    
    if watchlist_data:
        df_watch = pd.DataFrame(watchlist_data)
        
        # Color code signals
        def color_signal(val):
            if 'BUY' in val:
                return 'background-color: #90EE90'
            elif 'SELL' in val:
                return 'background-color: #FFB6C1'
            else:
                return 'background-color: #FFFFE0'
        
        styled_df = df_watch.style.applymap(color_signal, subset=['Signal'])
        st.dataframe(styled_df, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Use 5-minute intervals for intraday trading")
st.markdown("⚠️ **For educational purposes only** - Always verify signals before trading")
streamlit==1.28.1
yfinance==0.2.33
pandas==2.1.3
numpy==1.25.2
plotly==5.18.0
ta==0.10.2
packages.txt
