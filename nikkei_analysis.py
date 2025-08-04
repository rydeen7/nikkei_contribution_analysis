#!/usr/bin/env python3
"""
Nikkei 225 Analysis Tool
Complete Nikkei 225 index analysis with contribution calculations
"""

import warnings
warnings.filterwarnings('ignore')

# Import modules
from data_manager import NikkeiDataManager
from contribution_calculator import NikkeiContributionCalculator
from visualizer import NikkeiVisualizer
from market_cap_analyzer import MarketCapAnalyzer


def main():
    """Main analysis function"""
    print("🔥 NIKKEI 225 ANALYSIS TOOL 🔥")
    print("Real-time contribution analysis")
    print("=" * 60)
    
    try:
        # Initialize data manager
        data_manager = NikkeiDataManager()
        
        # Download master data
        if not data_manager.download_master_data():
            print("Failed to download master data")
            return
        
        # Load master data
        master_df = data_manager.load_master_data()
        if master_df is None:
            print("Failed to load master data")
            return
        
        # Download stock prices
        stock_prices = data_manager.download_stock_prices(master_df)
        if not stock_prices:
            print("Failed to download stock prices")
            return
        
        # Calculate contributions
        calculator = NikkeiContributionCalculator(data_manager.base_folder)
        results = calculator.calculate_all_contributions(data_manager)
        
        if results is None:
            print("Failed to calculate contributions")
            return
        
        # Skip chart generation (used only by web application)
        print("✓ Analysis completed successfully")
        
        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"📊 Data files saved in: ./{data_manager.base_folder}/")
        print("💹 Web application: python webapp.py")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Analysis interrupted by user")
    except Exception as e:
        print(f"\n💥 Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()