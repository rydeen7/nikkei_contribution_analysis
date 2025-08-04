"""
Nikkei Data Manager - Handles all data acquisition for Nikkei 225 analysis
"""

import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import os
import time
from datetime import datetime, timedelta
import json
import re

from config import DEFAULT_HEADERS, DEFAULT_BASE_FOLDER


class NikkeiDataManager:
    """Handles all data acquisition for Nikkei 225 analysis"""
    
    def __init__(self, base_folder=DEFAULT_BASE_FOLDER):
        self.base_folder = base_folder
        self.headers = DEFAULT_HEADERS
        
    def download_master_data(self):
        """Download all master data files"""
        print("=" * 50)
        print("DOWNLOADING MASTER DATA")
        print("=" * 50)
        
        try:
            # Create base folder
            os.makedirs(self.base_folder, exist_ok=True)
            print(f"✓ Created base folder: {self.base_folder}")
            
            # Download files (only price adjustment factors needed)
            files_to_download = [
                ("price_adjustment_factor.csv", "株価換算係数")
            ]
            
            for filename, description in files_to_download:
                self._download_file_from_nikkei(filename, description)
            
            # Convert downloaded files and create master_data.csv
            self._process_downloaded_files()
                
            return True
            
        except Exception as e:
            print(f"✗ Error downloading master data: {e}")
            return False
    
    def _download_file_from_nikkei(self, filename, description):
        """Download individual file from Nikkei website"""
        try:
            print(f"Downloading {description} ({filename})...")
            
            # Map filenames to their URLs
            url_mapping = {
                "price_adjustment_factor.csv": "https://indexes.nikkei.co.jp/nkave/archives/file/nikkei_225_price_adjustment_factor_jp.csv"
                # daily_data.csvの行を削除
            }
            
            url = url_mapping.get(filename)
            if not url:
                raise ValueError(f"No URL mapping found for {filename}")
            
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # Direct CSV download with encoding conversion
            file_path = os.path.join(self.base_folder, filename)
            
            # Try to decode and re-encode to fix character encoding
            try:
                # Try different encodings for decoding
                content_decoded = None
                for encoding in ['shift-jis', 'cp932', 'utf-8']:
                    try:
                        content_decoded = response.content.decode(encoding)
                        print(f"✓ Decoded {filename} with encoding: {encoding}")
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content_decoded is None:
                    # If decoding fails, save as binary
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                else:
                    # Save as UTF-8
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content_decoded)
                    
            except Exception as e:
                print(f"Encoding conversion failed for {filename}: {e}")
                # Fallback to binary save
                with open(file_path, 'wb') as f:
                    f.write(response.content)
            
            print(f"✓ Downloaded and processed: {file_path}")
            return True
                
        except Exception as e:
            print(f"✗ Error downloading {filename}: {e}")
            return False
    
    def _process_downloaded_files(self):
        """Process downloaded files and create master_data.csv"""
        try:
            print("Processing downloaded files and creating master_data.csv...")
            
            # Load price_adjustment_factor.csv
            price_factor_path = os.path.join(self.base_folder, "price_adjustment_factor.csv")
            
            # Try different encodings for the downloaded file
            for encoding in ['shift-jis', 'utf-8', 'cp932']:
                try:
                    df = pd.read_csv(price_factor_path, encoding=encoding)
                    df.columns = df.columns.str.strip()
                    print(f"✓ Loaded price_adjustment_factor.csv with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not decode price_adjustment_factor.csv with any encoding")
            
            # Create master_data.csv with proper structure (no date column needed)
            master_data = []
            
            for idx, row in df.iterrows():
                try:
                    # Skip rows with NaN values in critical fields
                    if pd.isna(row['コード']) or pd.isna(row['銘柄名']):
                        continue
                    
                    # Clean and convert code
                    code = str(row['コード']).strip().strip('"')
                    
                    try:
                        # Convert to int to remove decimal, then back to string
                        code = str(int(float(code)))
                    except (ValueError, TypeError):
                        continue  # Skip invalid codes
                    
                    # Clean other fields
                    name = str(row['銘柄名']).strip().strip('"')
                    sector = str(row['業種']).strip().strip('"') if not pd.isna(row['業種']) else 'Unknown'
                    category = str(row['セクター']).strip().strip('"') if 'セクター' in row and not pd.isna(row['セクター']) else 'Unknown'
                    
                    master_data.append({
                        'コード': code,
                        '銘柄名': name,
                        '株価換算係数': row['株価換算係数'],
                        '業種': sector,
                        'セクター': category
                    })
                    
                except Exception:
                    continue
            
            # Save master_data.csv
            master_df = pd.DataFrame(master_data)
            master_data_path = os.path.join(self.base_folder, "master_data.csv")
            master_df.to_csv(master_data_path, index=False, encoding='utf-8')
            
            print(f"✓ Created master_data.csv with {len(master_data)} stocks")
            return True
            
        except Exception as e:
            print(f"✗ Error processing downloaded files: {e}")
            return False
    
    def load_master_data(self):
        """Load and return master data"""
        try:
            master_data_path = os.path.join(self.base_folder, "master_data.csv")
            
            if not os.path.exists(master_data_path):
                print(f"Master data file not found: {master_data_path}")
                return None
            
            # Load with proper encoding
            # Try different encodings
            for encoding in ['utf-8', 'shift-jis', 'cp932']:
                try:
                    master_df = pd.read_csv(master_data_path, encoding=encoding)
                    master_df.columns = master_df.columns.str.strip()
                    print(f"✓ Loaded with encoding: {encoding}")
                    print(f"✓ Columns: {list(master_df.columns)}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not decode file with any encoding")
            
            print(f"✓ Master data loaded: {master_df.shape[0]} stocks")
            return master_df
            
        except Exception as e:
            print(f"✗ Error loading master data: {e}")
            return None
    
    def download_stock_prices(self, master_df):
        """Download stock prices for all companies in master data"""
        try:
            print("=" * 50)
            print("DOWNLOADING STOCK PRICES")
            print("=" * 50)
            
            # Create stock prices folder
            stock_prices_folder = os.path.join(self.base_folder, "stock_prices")
            os.makedirs(stock_prices_folder, exist_ok=True)
            
            all_prices = {}
            successful_downloads = 0
            
            for index, row in master_df.iterrows():
                stock_code = row['コード']
                company_name = row['銘柄名']
                
                print(f"Downloading prices for {stock_code} ({company_name})...")
                
                price_data = self._get_stock_price_yahoo_jp(stock_code)
                if price_data:
                    all_prices[stock_code] = price_data
                    successful_downloads += 1
                    print(f"✓ {stock_code}: ¥{price_data['current_price']:,.1f} ({price_data['change']:+.1f})")
                else:
                    print(f"✗ Failed to get price for {stock_code}")
                
                # Rate limiting
                time.sleep(0.1)
            
            # Save all prices to CSV in time-series format
            if all_prices:
                # Create a DataFrame with stock codes as columns and today's date as index
                today = pd.Timestamp.now().normalize()
                price_data = {}
                
                for code, data in all_prices.items():
                    price_data[code] = data['current_price']
                
                # Create DataFrame with date index
                prices_df = pd.DataFrame([price_data], index=[today])
                all_prices_path = os.path.join(stock_prices_folder, "all_stock_prices.csv")
                
                # If file exists, append new data
                if os.path.exists(all_prices_path):
                    existing_df = pd.read_csv(all_prices_path, index_col=0, parse_dates=True)
                    # Update or append today's data
                    if today in existing_df.index:
                        existing_df.loc[today] = price_data
                    else:
                        prices_df = pd.concat([existing_df, prices_df])
                
                prices_df.to_csv(all_prices_path, encoding='utf-8')
                
                print(f"\n✓ Stock prices saved: {all_prices_path}")
                print(f"✓ Successfully downloaded {successful_downloads}/{len(master_df)} stock prices")
                
                return all_prices
            else:
                print("✗ No stock prices downloaded")
                return {}
                
        except Exception as e:
            print(f"✗ Error downloading stock prices: {e}")
            return {}
    
    def _get_stock_price_yahoo_jp(self, stock_code):
        """Get current stock price from Yahoo Finance Japan"""
        try:
            # Construct Yahoo Finance Japan URL
            url = f"https://finance.yahoo.co.jp/quote/{stock_code}.T"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Method 1: Try JSON extraction method (more reliable)
            try:
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'window.__PRELOADED_STATE__' in script.string:
                        script_content = script.string
                        break
                else:
                    # Fall through to CSS selector method
                    raise Exception("No __PRELOADED_STATE__ found")
                
                # Extract JSON from the script using proper brace counting
                start_marker = 'window.__PRELOADED_STATE__ = '
                start_pos = script_content.find(start_marker)
                if start_pos == -1:
                    raise Exception("Could not find JSON start marker")
                
                json_start = start_pos + len(start_marker)
                
                # Find the closing of the JSON object by counting braces
                brace_count = 0
                json_end = json_start
                for i, char in enumerate(script_content[json_start:]):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            json_end = json_start + i + 1
                            break
                
                json_str = script_content[json_start:json_end]
                data = json.loads(json_str)
                
                # Navigate to the stock price data
                current_price = None
                prev_close = None
                change = None
                
                # Check mainStocksPriceBoard for current price
                if 'mainStocksPriceBoard' in data and data['mainStocksPriceBoard']:
                    price_board = data['mainStocksPriceBoard']
                    if 'priceBoard' in price_board and price_board['priceBoard']:
                        board_data = price_board['priceBoard']
                        
                        # Get save price (most recent trading price)
                        if 'savePrice' in board_data and board_data['savePrice']:
                            save_price_str = str(board_data['savePrice']).replace(',', '')
                            try:
                                current_price = float(save_price_str)
                            except ValueError:
                                pass
                        
                        # Try regular price field if savePrice not available
                        if current_price is None and 'price' in board_data and board_data['price'] != '---':
                            price_str = str(board_data['price']).replace(',', '')
                            try:
                                current_price = float(price_str)
                            except ValueError:
                                pass
                
                # Check mainStocksDetail for previous close
                if 'mainStocksDetail' in data and data['mainStocksDetail']:
                    stock_detail = data['mainStocksDetail']
                    if 'detail' in stock_detail and stock_detail['detail']:
                        detail_data = stock_detail['detail']
                        
                        # Get previous price
                        if 'previousPrice' in detail_data and detail_data['previousPrice']:
                            prev_price_str = str(detail_data['previousPrice']).replace(',', '')
                            try:
                                prev_close = float(prev_price_str)
                            except ValueError:
                                pass
                
                # Calculate change
                if current_price is not None and prev_close is not None:
                    change = current_price - prev_close
                
                if current_price is not None:
                    return {
                        'current_price': current_price,
                        'prev_close': prev_close,
                        'change': change or 0.0,
                        'timestamp': datetime.now()
                    }
            
            except Exception as json_error:
                print(f"JSON method failed for {stock_code}: {json_error}")
            
            # Method 2: Try CSS selectors as fallback
            try:
                # Look for price spans/divs with common class patterns
                price_selectors = [
                    'span._1fofaCjs',  # Main price display
                    'span[data-field="price"]',
                    '.stoksPrice',
                    'div._1Y3qLpB6 span:first-child',  # Alternative price location
                    '[data-test="price"]',
                    '.price',
                    'span[data-symbol]',
                    '.Fw\\(b\\)',  # Bold font weight class
                ]
                
                current_price = None
                for selector in price_selectors:
                    price_elem = soup.select_one(selector)
                    if price_elem:
                        price_text = price_elem.get_text().strip()
                        # Remove commas and extract numeric value
                        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
                        if price_match:
                            current_price = float(price_match.group().replace(',', ''))
                            break
                
                if current_price is not None:
                    return {
                        'current_price': current_price,
                        'prev_close': None,
                        'change': 0.0,
                        'timestamp': datetime.now()
                    }
            
            except Exception as css_error:
                print(f"CSS selector method failed for {stock_code}: {css_error}")
            
            print(f"Could not find price data for {stock_code}")
            return None
            
        except Exception as e:
            print(f"Error getting price for {stock_code}: {e}")
            return None
    
    def get_business_day_offset(self, date, offset_days):
        """Get business day with offset, skipping weekends"""
        current = date
        days_added = 0
        
        while days_added < abs(offset_days):
            if offset_days > 0:
                current += timedelta(days=1)
            else:
                current -= timedelta(days=1)
            
            # Skip weekends (Saturday=5, Sunday=6)
            if current.weekday() < 5:
                days_added += 1
        
        return current
    
    def get_realtime_nikkei_price(self):
        """Get real-time Nikkei 225 price from Nikkei website"""
        try:
            url = "https://www.nikkei.com/markets/worldidx/chart/nk225/"
            
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract price data based on discovered structure
            try:
                current_price = None
                prev_close = None
                open_price = None
                high_price = None
                low_price = None
                
                # Find current price using the economic_value_now class
                current_price_elem = soup.select_one('.economic_value_now')
                if current_price_elem:
                    current_text = current_price_elem.get_text().strip()
                    current_match = re.search(r'[\d,]+\.?\d*', current_text.replace(',', ''))
                    if current_match:
                        current_price = float(current_match.group().replace(',', ''))
                
                # Extract OHLC data from trend values with correct mapping
                trend_values = soup.select('.m-trend_economic_table_value')
                
                if len(trend_values) >= 4:
                    try:
                        # Based on investigation:
                        # Index 0: Open (始値)
                        # Index 1: High (高値)  
                        # Index 2: Low (安値)
                        # Index 3: Previous Close (前日終値)
                        
                        open_text = trend_values[0].get_text().strip()
                        open_match = re.search(r'[\d,]+\.?\d*', open_text.replace(',', ''))
                        if open_match:
                            open_price = float(open_match.group().replace(',', ''))
                        
                        high_text = trend_values[1].get_text().strip()
                        high_match = re.search(r'[\d,]+\.?\d*', high_text.replace(',', ''))
                        if high_match:
                            high_price = float(high_match.group().replace(',', ''))
                        
                        low_text = trend_values[2].get_text().strip()
                        low_match = re.search(r'[\d,]+\.?\d*', low_text.replace(',', ''))
                        if low_match:
                            low_price = float(low_match.group().replace(',', ''))
                        
                        prev_text = trend_values[3].get_text().strip()
                        prev_match = re.search(r'[\d,]+\.?\d*', prev_text.replace(',', ''))
                        if prev_match:
                            prev_close = float(prev_match.group().replace(',', ''))
                            
                    except (ValueError, IndexError) as e:
                        print(f"Error parsing trend values: {e}")
                        pass
                
                # If we have current price, use reasonable fallbacks for missing data
                if current_price is not None:
                    # Use yesterday's close from daily_data.csv if prev_close not found
                    if prev_close is None:
                        try:
                            daily_path = os.path.join(self.base_folder, "daily_data.csv")
                            if os.path.exists(daily_path):
                                for encoding in ['shift-jis', 'utf-8', 'cp932']:
                                    try:
                                        df = pd.read_csv(daily_path, encoding=encoding, skipfooter=1, engine='python')
                                        df.columns = df.columns.str.strip()
                                        if len(df) > 0:
                                            prev_close = float(df['終値'].iloc[-1])
                                        break
                                    except:
                                        continue
                        except:
                            pass
                    
                    # Use reasonable fallbacks for OHLC
                    if open_price is None:
                        open_price = prev_close if prev_close else current_price
                    if high_price is None:
                        high_price = max(current_price, prev_close) if prev_close else current_price
                    if low_price is None:
                        low_price = min(current_price, prev_close) if prev_close else current_price
                    
                    return {
                        'current_price': current_price,
                        'prev_close': prev_close,
                        'open': open_price,
                        'high': high_price,
                        'low': low_price,
                        'change': current_price - prev_close if prev_close else 0.0,
                        'timestamp': datetime.now()
                    }
                
            except Exception as parsing_error:
                print(f"Error parsing Nikkei website data: {parsing_error}")
            
            return None
            
        except Exception as e:
            print(f"✗ Error getting Nikkei price: {e}")
            return None
    
    def update_daily_data_with_current(self):
        """Update daily_data.csv with current day data if not already present"""
        try:
            daily_data_path = os.path.join(self.base_folder, "daily_data.csv")
            
            # Load existing daily data
            for encoding in ['shift-jis', 'utf-8', 'cp932']:
                try:
                    nikkei_df = pd.read_csv(daily_data_path, encoding=encoding, skipfooter=1, engine='python')
                    nikkei_df.columns = nikkei_df.columns.str.strip()
                    print(f"✓ Loaded daily_data.csv with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print("✗ Could not load daily_data.csv")
                return False
            
            # Parse dates
            nikkei_df['データ日付'] = pd.to_datetime(nikkei_df['データ日付'])
            
            # Check if today's data is already present
            today = pd.Timestamp.now().normalize()
            if today in nikkei_df['データ日付'].values:
                print(f"✓ Today's data ({today.strftime('%Y-%m-%d')}) already in daily_data.csv")
                return True
            
            # Get real-time Nikkei data
            nikkei_data = self.get_realtime_nikkei_price()
            if not nikkei_data:
                print("✗ Could not get real-time Nikkei data")
                return False
            
            print(f"✓ Got real-time Nikkei: {nikkei_data['current_price']:,.1f} ({nikkei_data['change']:+.1f})")
            
            # Create new row for today
            new_row = {
                'データ日付': today.strftime('%Y/%m/%d'),
                '始値': nikkei_data['open'],
                '高値': nikkei_data['high'],
                '安値': nikkei_data['low'],
                '終値': nikkei_data['current_price']
            }
            
            # Add new row to dataframe
            new_df = pd.DataFrame([new_row])
            updated_df = pd.concat([nikkei_df, new_df], ignore_index=True)
            
            # Save updated data
            updated_df.to_csv(daily_data_path, index=False, encoding='utf-8')
            print(f"✓ Added today's data to daily_data.csv")
            
            return True
            
        except Exception as e:
            print(f"✗ Error updating daily_data.csv: {e}")
            return False