#!/usr/bin/env python3
"""
Yahoo Finance Japan Stock Price Scraper

This module provides functionality to scrape real-time stock prices
from Yahoo Finance Japan using direct JSON extraction from web pages.
"""

import requests
import json
import re
import time

def get_stock_price_yahoo_jp(stock_code):
    """
    Get stock price from Yahoo Finance Japan
    
    Args:
        stock_code: Stock code (e.g., '8035' for Tokyo Electron)
    
    Returns:
        dict: Current price and previous close
    """
    url = f"https://finance.yahoo.co.jp/quote/{stock_code}.T"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        html_text = response.text
        
        # Find the start of PRELOADED_STATE
        start_marker = 'window.__PRELOADED_STATE__ = '
        start_pos = html_text.find(start_marker)
        
        if start_pos == -1:
            print(f"Could not find PRELOADED_STATE marker for {stock_code}")
            return None
        
        # Move to the start of the JSON
        start_pos += len(start_marker)
        
        # Find the end by counting braces
        brace_count = 0
        in_string = False
        escape_next = False
        end_pos = start_pos
        
        for i in range(start_pos, min(start_pos + 500000, len(html_text))):  # Limit search
            char = html_text[i]
            
            if escape_next:
                escape_next = False
                continue
                
            if char == '\\':
                escape_next = True
                continue
                
            if char == '"' and not escape_next:
                in_string = not in_string
                continue
                
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end_pos = i + 1
                        break
        
        if brace_count != 0:
            print(f"Could not find complete JSON for {stock_code}")
            return None
        
        # Extract and parse JSON
        json_str = html_text[start_pos:end_pos]
        
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"JSON decode error for {stock_code}: {e}")
            return None
        
        # Extract stock data
        result = {
            'code': stock_code,
            'url': url,
            'name': None,
            'market': None,
            'current_price': None,
            'previous_close': None,
            'change': None,
            'change_percent': None
        }
        
        # Navigate the JSON structure
        if 'mainStocksPriceBoard' in data and 'priceBoard' in data['mainStocksPriceBoard']:
            pb = data['mainStocksPriceBoard']['priceBoard']
            
            result['name'] = pb.get('name', '')
            result['market'] = pb.get('marketName', '')
            
            # Current price
            price_str = pb.get('price', '')
            if price_str and price_str != '---':
                try:
                    # Handle both integer and decimal prices
                    clean_price = price_str.replace(',', '').replace('円', '').strip()
                    result['current_price'] = float(clean_price)
                except ValueError:
                    pass
            
            # Price change
            change_str = pb.get('priceChange', '')
            if change_str and change_str != '---':
                try:
                    # Handle both positive and negative changes with decimals
                    clean_change = change_str.replace(',', '').replace('円', '').strip()
                    result['change'] = float(clean_change)
                except ValueError:
                    pass
            
            # Change percent
            rate_str = pb.get('priceChangeRate', '')
            if rate_str and rate_str != '---':
                try:
                    # Handle percentage values
                    clean_rate = rate_str.replace(',', '').replace('%', '').strip()
                    result['change_percent'] = float(clean_rate)
                except ValueError:
                    pass
        
        # Get previous close from detail section
        if 'mainStocksDetail' in data and 'detail' in data['mainStocksDetail']:
            detail = data['mainStocksDetail']['detail']
            
            prev_str = detail.get('previousPrice', '')
            if prev_str and prev_str != '---':
                try:
                    # Handle decimal values in previous close
                    clean_prev = prev_str.replace(',', '').replace('円', '').strip()
                    result['previous_close'] = float(clean_prev)
                except ValueError:
                    pass
        
        return result
        
    except requests.RequestException as e:
        print(f"Network error for {stock_code}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {stock_code}: {e}")
        return None

def main():
    """Test the scraper"""
    print("Yahoo Finance Japan Scraper - Final Version")
    print("=" * 60)
    
    test_stocks = [
        ('8035', '東京エレクトロン'),
        ('7203', 'トヨタ自動車'), 
        ('6758', 'ソニーグループ'),
        ('9984', 'ソフトバンクグループ')
    ]
    
    successful_count = 0
    
    for code, expected_name in test_stocks:
        print(f"\n[{code}] {expected_name}")
        print("-" * 40)
        
        result = get_stock_price_yahoo_jp(code)
        
        if result and result['current_price']:
            successful_count += 1
            print(f"会社名: {result['name']}")
            print(f"市場: {result['market']}")
            # Display price with appropriate decimal places
            if result['current_price'] % 1 == 0:
                print(f"現在値: ¥{result['current_price']:,.0f}")
            else:
                print(f"現在値: ¥{result['current_price']:,.1f}")
            
            if result['previous_close']:
                if result['previous_close'] % 1 == 0:
                    print(f"前日終値: ¥{result['previous_close']:,.0f}")
                else:
                    print(f"前日終値: ¥{result['previous_close']:,.1f}")
                
            if result['change'] is not None and result['change_percent'] is not None:
                if result['change'] % 1 == 0:
                    print(f"前日比: ¥{result['change']:+,.0f} ({result['change_percent']:+.2f}%)")
                else:
                    print(f"前日比: ¥{result['change']:+,.1f} ({result['change_percent']:+.2f}%)")
        else:
            print("データ取得失敗")
        
        time.sleep(0.5)  # Rate limiting
    
    print(f"\n\n成功率: {successful_count}/{len(test_stocks)}")

if __name__ == "__main__":
    main()