import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
import os

def get_stock_data(ticker_str="DIS"):
    try:
        ticker = yf.Ticker(ticker_str)
        hist = ticker.history(period="7d")
        if hist.empty:
            return None
        close = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2] if len(hist) > 1 else close
        change = (close - prev) / prev * 100 if prev != 0 else 0
        # 그래프 저장
        plt.figure(figsize=(4, 1.2))
        plt.plot(hist['Close'], linewidth=2.5)
        plt.axis('off')
        plt.tight_layout()
        chart_path = f"/tmp/{ticker_str}_chart.png"
        plt.savefig(chart_path, transparent=True, dpi=200, bbox_inches='tight')
        plt.close()
        return {
            "ticker": ticker_str,
            "close": float(close),
            "change": float(change),
            "history": hist['Close'].tolist(),
            "chart_path": chart_path,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
    except Exception as e:
        print(f"stock error {ticker_str}: {e}")
        return {
            "ticker": ticker_str,
            "close": 0,
            "change": 0,
            "history": [],
            "chart_path": None,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
