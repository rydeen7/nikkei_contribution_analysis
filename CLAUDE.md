# Nikkei 225 Analysis Tool

This project provides comprehensive real-time analysis of Nikkei 225 index movements, including daily price analysis, individual stock contributions, and sector/industry breakdowns.

## Features

- **Real-time Data Analysis**: Downloads latest data from official Nikkei sources and Yahoo Finance Japan
- **Stock Price Scraping**: Real-time individual stock price tracking via Yahoo Finance Japan web scraping
- **Contribution Calculations**: Precise calculation using relative contribution methodology
- **Web Application**: FastAPI-based dashboard with real-time analysis and professional visualizations
- **Market Cap Analysis**: Top 20 TOPIX market cap stocks price change tracking

## Architecture

### Modular Design

The application is organized into separate modules for better maintainability:

```
nikkei/
├── data_manager.py          # Data acquisition and management
├── contribution_calculator.py # Contribution calculation logic
├── visualizer.py            # Chart data preparation
├── market_cap_analyzer.py   # Market cap top 20 analysis
├── yahoo_jp_scraper.py      # Yahoo Finance Japan scraper
├── config.py               # Configuration and constants
├── webapp.py               # FastAPI web application
├── nikkei_analysis.py      # Standalone CLI application
└── static/                 # Web assets (JS, CSS)
    ├── js/
    │   ├── charts.js       # Chart.js implementations
    │   ├── api.js          # API communication
    │   └── main.js         # Main application logic
    └── css/
        └── style.css       # Styling
```

### Key Components

1. **NikkeiDataManager** (`data_manager.py`)
   - Downloads master data from Nikkei (price adjustment factors)
   - Creates master_data.csv from price_adjustment_factor.csv
   - Scrapes real-time stock prices from Yahoo Finance Japan
   - Fetches real-time Nikkei 225 index data
   - Manages business day calculations

2. **NikkeiContributionCalculator** (`contribution_calculator.py`)
   - Calculates individual stock contributions
   - Computes sector and industry level contributions
   - Uses relative contribution methodology
   - Formula: `個別寄与度 = 日経平均変化幅 × (個別株加重変化幅 / 全銘柄加重変化幅合計)`

3. **NikkeiVisualizer** (`visualizer.py`)
   - Prepares chart data for web visualization
   - Formats data for Chart.js consumption
   - Handles Japanese text properly

4. **MarketCapAnalyzer** (`market_cap_analyzer.py`)
   - Analyzes TOPIX top 20 market cap stocks
   - Fetches real-time price changes
   - Provides data for market cap chart

5. **YahooJPScraper** (`yahoo_jp_scraper.py`)
   - Scrapes real-time stock prices from Yahoo Finance Japan
   - Handles Japanese encoding properly
   - Extracts data from JavaScript objects in HTML

## Quick Start

### Local Execution

1. **Install Dependencies** (managed by uv)
   ```bash
   uv sync
   ```

2. **Run Standalone Analysis**
   ```bash
   uv run python nikkei_analysis.py
   ```

3. **Run Web Application**
   ```bash
   uv run python webapp.py
   ```
   Then open http://localhost:8001 in your browser

### Web Application Features

- **Run Analysis**: Execute complete analysis with latest data
- **Refresh Data**: Re-display charts with existing analysis results
- **Three Main Charts**:
  1. Industry Contributions (業種別寄与度)
  2. Individual Stock Contributions (個別銘柄寄与度 - Top 10/Bottom 10)
  3. Market Cap Top 20 Price Changes (時価総額上位20銘柄 前日比変動率)

## Output Files

### Data Files
All data files are saved in `./nikkei_local/`:
- `price_adjustment_factor.csv` - Downloaded from Nikkei
- `master_data.csv` - Processed master data with stock information
- `stock_prices/all_stock_prices.csv` - Real-time stock prices

### Contribution Results
Saved in `./nikkei_local/contributions/`:
- `stock_contributions.csv` - Individual stock contributions
- `sector_contributions.csv` - Sector-level contributions
- `industry_contributions.csv` - Industry-level contributions

## Methodology

### Contribution Calculation
The tool uses relative contribution methodology:

```
Individual Stock Contribution = Nikkei Daily Change × (Stock Weighted Change / Total Weighted Change)
```

Where:
- Stock Weighted Change = Stock Price Change × Adjustment Factor (株価換算係数)
- Total Weighted Change = Sum of all Stock Weighted Changes

### Data Sources
- **Nikkei Official**: https://indexes.nikkei.co.jp/
- **Stock Prices**: Yahoo Finance Japan (https://finance.yahoo.co.jp/)
- **Real-time Nikkei**: Nikkei website (https://www.nikkei.com/)

### Processing Flow
1. Download price adjustment factors from Nikkei
2. Create master data with stock information
3. Scrape individual stock prices from Yahoo Finance Japan
4. Fetch real-time Nikkei 225 index price
5. Calculate contributions using relative methodology
6. Export results to CSV files
7. Serve results via web application

## Technical Details

### Dependencies Management
- **uv**: Modern Python package manager
- **pyproject.toml**: Project configuration and dependencies
- **uv.lock**: Locked dependencies for reproducible environments

### Key Dependencies
- pandas: Data manipulation
- numpy: Numerical calculations
- beautifulsoup4: Web scraping
- fastapi: Web framework
- uvicorn: ASGI server
- Chart.js: Client-side charting (loaded via CDN)

### Japanese Text Handling
- Automatic encoding detection (Shift-JIS, UTF-8, CP932)
- Proper display of Japanese company and industry names
- Web application fully supports Japanese text

### Error Handling
- Retry logic for network requests
- Fallback for real-time data failures
- Graceful handling of non-trading days
- Detailed error logging

## API Endpoints

- `GET /`: Main dashboard page
- `POST /api/analyze`: Run complete analysis
- `GET /api/data`: Get current analysis data
- `GET /api/market-cap`: Get market cap top 20 data
- `GET /api/status`: Get analysis status

## Recent Updates

### 2025-08-04 (Latest)
- **Major Refactoring**:
  - Modularized codebase into separate components
  - Removed dependency on historical daily_data.csv
  - Simplified to use only real-time data
  - Fixed DataFrame performance warnings
  - Removed candlestick chart (30-day historical view)
- **Enhanced Market Cap Analysis**:
  - Integrated TOPIX top 20 market cap stocks
  - Added real-time price change tracking
  - Market cap data updates with Run Analysis button
- **Improved Error Handling**:
  - Better string/integer type handling for stock codes
  - Fixed contribution calculation errors
  - Enhanced web scraping reliability

### Previous Updates
- Replaced yfinance with Yahoo Finance Japan scraping
- Added FastAPI web application
- Implemented real-time Nikkei price integration
- Fixed Japanese font rendering issues

## Troubleshooting

### Common Issues

1. **No data on weekends/holidays**: The tool will show the latest available trading day data
2. **Stock price scraping failures**: Check Yahoo Finance Japan accessibility
3. **Contribution calculation errors**: Ensure all required files are downloaded
4. **Web application not loading**: Check if port 8001 is available

### Debug Mode

For detailed debugging, check console output which includes:
- Download progress for each stock
- Calculation steps
- Any errors with full traceback

## License

This tool is for educational and research purposes. Please respect data provider terms of service.

## Notes

- Real-time data during trading hours (9:00-15:00 JST)
- Yahoo Finance Japan data may have slight delays
- Nikkei official data updates after market close
- All timestamps are in JST