"""
Nikkei Contribution Calculator - Performs all contribution calculations
"""

import pandas as pd
import numpy as np
import os


class NikkeiContributionCalculator:
    """Handles all contribution calculations for Nikkei 225 analysis"""
    
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.contributions_folder = os.path.join(folder_path, "contributions")
        
    def _load_data(self):
        """Load all necessary data files"""
        try:
            # Load stock prices (may not exist yet for new format)
            stock_prices_path = os.path.join(self.folder_path, "stock_prices", "all_stock_prices.csv")
            if os.path.exists(stock_prices_path):
                stock_prices_df = pd.read_csv(stock_prices_path, index_col=0, parse_dates=True)
                print(f"✓ Stock prices loaded: {stock_prices_df.shape}")
            else:
                # Return None for stock_prices_df if file doesn't exist
                stock_prices_df = None
                print("ℹ Stock prices file not found (will be created during download)")
            
            # Load master data
            master_data_path = os.path.join(self.folder_path, "master_data.csv")
            # Try different encodings
            for encoding in ['shift-jis', 'utf-8', 'cp932']:
                try:
                    master_df = pd.read_csv(master_data_path, encoding=encoding)
                    master_df.columns = master_df.columns.str.strip()
                    break
                except UnicodeDecodeError:
                    continue
            
            # Load Nikkei daily data
            nikkei_daily_path = os.path.join(self.folder_path, "daily_data.csv")
            
            # Try different encodings for daily_data.csv
            for encoding in ['shift-jis', 'utf-8', 'cp932']:
                try:
                    nikkei_df = pd.read_csv(nikkei_daily_path, encoding=encoding, skipfooter=1, engine='python')
                    nikkei_df.columns = nikkei_df.columns.str.strip()
                    print(f"✓ Loaded daily_data.csv with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                raise ValueError("Could not decode daily_data.csv with any encoding")
            nikkei_df['データ日付'] = pd.to_datetime(nikkei_df['データ日付'])
            nikkei_df.set_index('データ日付', inplace=True)
            
            return stock_prices_df, master_df, nikkei_df
            
        except Exception as e:
            print(f"✗ Error loading data: {e}")
            return None, None, None
    
    def _create_adjustment_factor_mapping(self, master_df):
        """Create mapping of stock codes to adjustment factors"""
        adjustment_factors = {}
        for _, row in master_df.iterrows():
            try:
                code = str(row['コード']).strip()
                factor = float(row['株価換算係数'])
                adjustment_factors[code] = factor
            except (ValueError, TypeError):
                # Skip invalid entries
                continue
        return adjustment_factors
    
    def _find_matching_column(self, code, columns):
        """Find matching column for stock code"""
        code_str = str(code)
        code_int = int(code) if isinstance(code, str) and code.isdigit() else code
        
        for col in columns:
            # Try exact string match first
            if str(col) == code_str:
                return col
            # Try integer comparison
            try:
                col_int = int(col) if isinstance(col, str) and col.isdigit() else col
                if col_int == code_int:
                    return col
            except (ValueError, TypeError):
                continue
        return None
    
    def _calculate_individual_contributions(self, price_changes, master_df, adjustment_factors, nikkei_changes):
        """Calculate individual stock contributions using relative method"""
        try:
            # Prepare to collect all contributions
            all_contributions = []
            
            for date in price_changes.index:
                date_contributions = {}
                daily_price_changes = price_changes.loc[date]
                nikkei_change = float(nikkei_changes.get(date, 0))
                
                # Calculate weighted changes for all stocks
                total_weighted_change = 0.0
                weighted_changes = {}
                
                for code in adjustment_factors.keys():
                    matching_col = self._find_matching_column(code, daily_price_changes.index)
                    if matching_col is not None and pd.notna(daily_price_changes[matching_col]):
                        try:
                            # Ensure numeric types
                            price_change = float(daily_price_changes[matching_col])
                            factor = float(adjustment_factors[code])
                            weighted_change = price_change * factor
                            weighted_changes[code] = weighted_change
                            total_weighted_change += weighted_change
                        except (ValueError, TypeError):
                            # Skip if conversion fails
                            continue
                
                # Calculate individual contributions using relative method
                for code, weighted_change in weighted_changes.items():
                    try:
                        if abs(total_weighted_change) > 1e-10:  # Avoid division by very small numbers
                            contribution = float(nikkei_change) * (float(weighted_change) / float(total_weighted_change))
                            date_contributions[str(code)] = contribution
                        else:
                            date_contributions[str(code)] = 0.0
                    except (ValueError, TypeError, ZeroDivisionError):
                        date_contributions[str(code)] = 0.0
                
                # Add date to the contributions
                date_contributions['date'] = date
                all_contributions.append(date_contributions)
            
            # Create DataFrame from list of dictionaries
            if all_contributions:
                df = pd.DataFrame(all_contributions)
                df.set_index('date', inplace=True)
                # Fill NaN values with 0
                df = df.fillna(0)
                return df
            else:
                return pd.DataFrame()
            
        except Exception as e:
            print(f"✗ Error calculating individual contributions: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def _calculate_sector_industry_contributions(self, stock_contributions, master_df):
        """Calculate sector and industry level contributions"""
        try:
            # Create mappings
            sector_mapping = {}
            industry_mapping = {}
            
            for _, row in master_df.iterrows():
                code = str(row['コード'])
                sector = row['セクター']
                industry = row['業種']
                sector_mapping[code] = sector
                industry_mapping[code] = industry
            
            # Calculate sector contributions
            sector_contributions = pd.DataFrame(index=stock_contributions.index)
            industry_contributions = pd.DataFrame(index=stock_contributions.index)
            
            for date in stock_contributions.index:
                sector_sums = {}
                industry_sums = {}
                
                for code in stock_contributions.columns:
                    if pd.notna(stock_contributions.loc[date, code]):
                        contribution = stock_contributions.loc[date, code]
                        
                        # Sector
                        sector = sector_mapping.get(code, 'Unknown')
                        if sector not in sector_sums:
                            sector_sums[sector] = 0
                        sector_sums[sector] += contribution
                        
                        # Industry
                        industry = industry_mapping.get(code, 'Unknown')
                        if industry not in industry_sums:
                            industry_sums[industry] = 0
                        industry_sums[industry] += contribution
                
                # Add to dataframes
                for sector, sum_val in sector_sums.items():
                    sector_contributions.loc[date, sector] = sum_val
                
                for industry, sum_val in industry_sums.items():
                    industry_contributions.loc[date, industry] = sum_val
            
            return sector_contributions, industry_contributions
            
        except Exception as e:
            print(f"✗ Error calculating sector/industry contributions: {e}")
            return pd.DataFrame(), pd.DataFrame()
    
    def calculate_all_contributions(self, data_manager=None, stock_prices_dict=None, nikkei_change=None):
        """Calculate all contribution analyses using real-time data only"""
        try:
            print("=" * 50)
            print("CALCULATING CONTRIBUTIONS")
            print("=" * 50)
            
            # Load master data only (no daily data needed)
            master_data_path = os.path.join(self.folder_path, "master_data.csv")
            for encoding in ['shift-jis', 'utf-8', 'cp932']:
                try:
                    master_df = pd.read_csv(master_data_path, encoding=encoding)
                    master_df.columns = master_df.columns.str.strip()
                    print(f"✓ Master data loaded with encoding: {encoding}")
                    break
                except UnicodeDecodeError:
                    continue
            else:
                print("✗ Failed to load master data")
                return None
            
            print(f"Master data codes: {list(master_df['コード'].head())}")
            
            # Create contributions folder
            os.makedirs(self.contributions_folder, exist_ok=True)
            
            # Create adjustment factor mapping
            adjustment_factors = self._create_adjustment_factor_mapping(master_df)
            print(f"✓ Adjustment factors created: {len(adjustment_factors)} stocks")
            
            # Get price changes from stock_prices_dict
            if not stock_prices_dict:
                print("✗ Stock prices dict not provided")
                return None
            
            # Use the dictionary passed from webapp
            price_changes_dict = {}
            for code, data in stock_prices_dict.items():
                if 'change' in data and pd.notna(data['change']):
                    price_changes_dict[str(code)] = float(data['change'])
            
            # Create a DataFrame with today's date
            today = pd.Timestamp.now().normalize()
            price_changes = pd.DataFrame([price_changes_dict], index=[today])
            print(f"✓ Price changes from dict: {len(price_changes_dict)} stocks")
            print(f"✓ Price changes prepared: {price_changes.shape}")
            
            # Use provided Nikkei change (from real-time data)
            if nikkei_change is None:
                print("✗ Nikkei change not provided")
                return None
            
            # Create simple dict with today's Nikkei change
            nikkei_changes_dict = {today: float(nikkei_change)}
            print(f"✓ Using Nikkei change: {nikkei_change:+.1f}")
            
            # Calculate individual stock contributions
            stock_contributions = self._calculate_individual_contributions(
                price_changes, master_df, adjustment_factors, nikkei_changes_dict
            )
            
            if stock_contributions.empty:
                print("✗ Failed to calculate stock contributions")
                return None
            
            print(f"✓ Individual stock contributions calculated: {stock_contributions.shape}")
            
            # Calculate sector and industry contributions
            sector_contributions, industry_contributions = self._calculate_sector_industry_contributions(
                stock_contributions, master_df
            )
            
            print(f"✓ Sector contributions calculated: {sector_contributions.shape}")
            print(f"✓ Industry contributions calculated: {industry_contributions.shape}")
            
            # Save results
            results = {
                'stock_contributions': stock_contributions,
                'sector_contributions': sector_contributions,
                'industry_contributions': industry_contributions
            }
            
            for name, df in results.items():
                if not df.empty:
                    output_path = os.path.join(self.contributions_folder, f"{name}.csv")
                    df.to_csv(output_path, encoding='utf-8')
                    print(f"✓ Saved: {output_path}")
            
            print("Contribution calculations completed successfully\n")
            return results
            
        except Exception as e:
            print(f"✗ Error in contribution calculations: {e}")
            import traceback
            traceback.print_exc()
            return None