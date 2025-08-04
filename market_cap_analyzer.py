"""
Market Cap Analyzer - Analyzes top market cap stocks
"""

import pandas as pd
import time
from config import TOP_20_MARKET_CAP
from yahoo_jp_scraper import get_stock_price_yahoo_jp


class MarketCapAnalyzer:
    """Handles market cap top stocks analysis"""
    
    def __init__(self):
        self.top20_stocks = TOP_20_MARKET_CAP
    
    def get_top20_price_changes(self):
        """Get price changes for top 20 market cap stocks"""
        
        print("=" * 50)
        print("FETCHING TOP 20 STOCKS PRICE CHANGES")
        print("=" * 50)
        
        results = []
        
        for i, (code, name) in enumerate(self.top20_stocks, 1):
            print(f"{i}. Fetching data for {code} ({name})...")
            
            try:
                # Get stock data from Yahoo Finance Japan
                stock_data = get_stock_price_yahoo_jp(code)
                
                if stock_data and stock_data['current_price']:
                    current_price = stock_data['current_price']
                    change = stock_data['change'] if stock_data['change'] is not None else 0
                    change_pct = stock_data['change_percent'] if stock_data['change_percent'] is not None else 0
                    
                    results.append({
                        'rank': i,
                        'code': code,
                        'name': name,
                        'price': current_price,
                        'change': change,
                        'change_pct': change_pct
                    })
                    
                    print(f"  ✓ Price: ¥{current_price:,.1f}")
                    print(f"  ✓ Change: {change:+.1f} ({change_pct:+.2f}%)")
                else:
                    print(f"  ✗ Failed to get price data")
                    results.append({
                        'rank': i,
                        'code': code,
                        'name': name,
                        'price': 0,
                        'change': 0,
                        'change_pct': 0
                    })
                
                # Rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                results.append({
                    'rank': i,
                    'code': code,
                    'name': name,
                    'price': 0,
                    'change': 0,
                    'change_pct': 0
                })
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Display summary
        print("\n" + "=" * 50)
        print("SUMMARY")
        print("=" * 50)
        
        valid_results = [r for r in results if r['price'] > 0]
        if valid_results:
            print(f"✓ Successfully fetched {len(valid_results)}/{len(self.top20_stocks)} stocks")
            
            # Sort by change percentage
            df_valid = df[df['price'] > 0].copy()
            df_sorted = df_valid.sort_values('change_pct', ascending=False)
            
            print("\n📈 TOP GAINERS:")
            for _, row in df_sorted.head(5).iterrows():
                if row['change_pct'] > 0:
                    print(f"  {row['code']} {row['name']}: {row['change_pct']:+.2f}%")
            
            print("\n📉 TOP LOSERS:")
            for _, row in df_sorted.tail(5).iterrows():
                if row['change_pct'] < 0:
                    print(f"  {row['code']} {row['name']}: {row['change_pct']:+.2f}%")
        
        return df
    
    def get_chart_data_json(self):
        """Get chart data for web application"""
        
        # Get price changes
        df = self.get_top20_price_changes()
        
        # Sort by market cap rank (already in order)
        # But keep only stocks with valid data
        df_valid = df[df['price'] > 0].copy()
        
        # Create chart data
        chart_data = {
            'labels': df_valid['name'].tolist(),
            'values': df_valid['change_pct'].tolist(),
            'codes': df_valid['code'].tolist()
        }
        
        return chart_data