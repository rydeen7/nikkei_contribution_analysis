"""
Nikkei Visualizer - Provides chart data for web application
"""

import pandas as pd
import os
from datetime import datetime


class NikkeiVisualizer:
    """Handles all visualization and charting for Nikkei 225 analysis"""
    
    def __init__(self, folder_path):
        self.folder_path = folder_path
        
    def get_chart_data_json(self, results, master_df, data_manager=None):
        """Get chart data in JSON format for web application"""
        try:
            print("Creating chart data for web application...")
            if results:
                print(f"Results keys: {list(results.keys())}")
                for key in results:
                    if hasattr(results[key], 'shape'):
                        print(f"  {key}: shape={results[key].shape}")
            else:
                print("Results is None or empty")
            chart_data = {}
            
            if results and 'industry_contributions' in results and not results['industry_contributions'].empty:
                print(f"Processing industry contributions, shape: {results['industry_contributions'].shape}")
                # Industry contributions
                # Ensure index is datetime
                if not isinstance(results['industry_contributions'].index, pd.DatetimeIndex):
                    results['industry_contributions'].index = pd.to_datetime(results['industry_contributions'].index)
                latest_date = results['industry_contributions'].index[-1]
                print(f"Latest date: {latest_date}")
                industry_contribs = results['industry_contributions'].loc[latest_date].dropna()
                print(f"Industry contributions: {len(industry_contribs)} items")
                
                # Keep Japanese industry names and sort by absolute value (descending)
                sorted_industry = industry_contribs.reindex(industry_contribs.abs().sort_values(ascending=False).index)
                
                chart_data['industry_contributions'] = {
                    'labels': sorted_industry.index.tolist(),
                    'values': sorted_industry.values.tolist()
                }
                
                # Individual stock contributions (top 10 and bottom 10)
                if 'stock_contributions' in results and not results['stock_contributions'].empty:
                    # Ensure index is datetime
                    if not isinstance(results['stock_contributions'].index, pd.DatetimeIndex):
                        results['stock_contributions'].index = pd.to_datetime(results['stock_contributions'].index)
                    stock_contribs = results['stock_contributions'].loc[latest_date].dropna()
                    
                    # Get top 10 positive and bottom 10 negative
                    positive_contribs = stock_contribs[stock_contribs > 0].sort_values(ascending=False).head(10)
                    negative_contribs = stock_contribs[stock_contribs < 0].sort_values(ascending=True).head(10)
                    
                    # Combine: positive (descending) + negative (ascending = most negative first)
                    top_stocks = pd.concat([positive_contribs, negative_contribs])
                    
                    # Convert stock codes to Japanese company names
                    stock_labels = []
                    for code in top_stocks.index:
                        company_row = master_df[master_df['コード'] == int(code)]
                        if not company_row.empty:
                            company_name = company_row['銘柄名'].iloc[0]
                            stock_labels.append(company_name)
                        else:
                            stock_labels.append(code)  # Fallback to code if name not found
                    
                    chart_data['stock_contributions'] = {
                        'labels': stock_labels,
                        'values': top_stocks.values.tolist()
                    }
                
                chart_data['last_updated'] = latest_date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # Provide empty data if results not available
                chart_data['industry_contributions'] = {'labels': [], 'values': []}
                chart_data['stock_contributions'] = {'labels': [], 'values': []}
                chart_data['last_updated'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            
            return chart_data
            
        except Exception as e:
            print(f"✗ Error creating chart data JSON: {e}")
            import traceback
            traceback.print_exc()
            # Return minimal valid data structure
            return {
                'industry_contributions': {'labels': [], 'values': []},
                'stock_contributions': {'labels': [], 'values': []},
                'last_updated': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
            }