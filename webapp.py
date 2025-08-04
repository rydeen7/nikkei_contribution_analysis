#!/usr/bin/env python3
"""
Nikkei 225 Analysis Web Application
FastAPI server for real-time chart display with static files
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import json
import os
from datetime import datetime
import asyncio
import threading

from data_manager import NikkeiDataManager
from contribution_calculator import NikkeiContributionCalculator
from visualizer import NikkeiVisualizer
from market_cap_analyzer import MarketCapAnalyzer

app = FastAPI(
    title="Nikkei 225 Real-time Analysis", 
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Templates
template_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=template_dir)

# Global variables to store analysis results
current_data = None
analysis_running = False
last_update = None

class NikkeiAnalysisService:
    """Service class to handle Nikkei analysis operations"""
    
    def __init__(self):
        self.data_manager = None
        self.calculator = None
        self.visualizer = None
        self.market_cap_analyzer = MarketCapAnalyzer()
        
    def run_analysis(self):
        """Run complete Nikkei analysis"""
        try:
            print("Starting Nikkei 225 analysis...")
            
            # Initialize components
            self.data_manager = NikkeiDataManager()
            
            # Download master data (price adjustment factors)
            self.data_manager.download_master_data()
            
            # Load master data
            master_df = self.data_manager.load_master_data()
            if master_df is None:
                raise Exception("Failed to load master data")
            
            # Download stock prices
            stock_prices = self.data_manager.download_stock_prices(master_df)
            if not stock_prices:
                raise Exception("Failed to download stock prices")
            
            # Get real-time Nikkei data
            nikkei_data = self.data_manager.get_realtime_nikkei_price()
            if not nikkei_data:
                raise Exception("Failed to get real-time Nikkei data")
            
            nikkei_change = nikkei_data['change']
            print(f"✓ Real-time Nikkei change: {nikkei_change:+.1f}")
            
            # Calculate contributions
            self.calculator = NikkeiContributionCalculator(self.data_manager.base_folder)
            results = self.calculator.calculate_all_contributions(self.data_manager, stock_prices, nikkei_change)
            
            if results is None:
                raise Exception("Failed to calculate contributions")
            
            # Generate chart data
            self.visualizer = NikkeiVisualizer(self.data_manager.base_folder)
            chart_data = self.visualizer.get_chart_data_json(results, master_df, self.data_manager)
            
            # Get market cap data
            market_cap_data = self.market_cap_analyzer.get_chart_data_json()
            chart_data['market_cap_changes'] = market_cap_data
            
            print("✓ Analysis completed successfully")
            return chart_data
            
        except Exception as e:
            print(f"✗ Analysis failed: {e}")
            raise e
    
    def get_existing_data(self):
        """Get existing analysis data without running new analysis"""
        try:
            if not self.data_manager:
                self.data_manager = NikkeiDataManager()
            
            # Check if analysis files exist
            master_data_path = os.path.join(self.data_manager.base_folder, "price_adjustment_factor.csv")
            contributions_path = os.path.join(self.data_manager.base_folder, "contributions", "stock_contributions.csv")
            
            if not os.path.exists(master_data_path) or not os.path.exists(contributions_path):
                return None
            
            # Load master data
            master_df = self.data_manager.load_master_data()
            if master_df is None:
                return None
            
            # Load existing results
            import pandas as pd
            
            stock_contributions = pd.read_csv(contributions_path, index_col=0, parse_dates=True)
            sector_contributions_path = os.path.join(self.data_manager.base_folder, "contributions", "sector_contributions.csv")
            industry_contributions_path = os.path.join(self.data_manager.base_folder, "contributions", "industry_contributions.csv")
            
            sector_contributions = pd.read_csv(sector_contributions_path, index_col=0, parse_dates=True) if os.path.exists(sector_contributions_path) else pd.DataFrame()
            industry_contributions = pd.read_csv(industry_contributions_path, index_col=0, parse_dates=True) if os.path.exists(industry_contributions_path) else pd.DataFrame()
            
            results = {
                'stock_contributions': stock_contributions,
                'sector_contributions': sector_contributions,
                'industry_contributions': industry_contributions
            }
            
            # Generate chart data
            if not self.visualizer:
                self.visualizer = NikkeiVisualizer(self.data_manager.base_folder)
            
            chart_data = self.visualizer.get_chart_data_json(results, master_df, self.data_manager)
            
            # Get market cap data
            market_cap_data = self.market_cap_analyzer.get_chart_data_json()
            chart_data['market_cap_changes'] = market_cap_data
            
            return chart_data
            
        except Exception as e:
            print(f"Error loading existing data: {e}")
            return None

# Global service instance
analysis_service = NikkeiAnalysisService()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main dashboard page"""
    try:
        print(f"Template directory: {template_dir}")
        print(f"Template exists: {os.path.exists(os.path.join(template_dir, 'index.html'))}")
        return templates.TemplateResponse("index.html", {"request": request})
    except Exception as e:
        print(f"Template error: {e}")
        return HTMLResponse(f"<h1>Template Error: {e}</h1>", status_code=500)

@app.post("/api/analyze")
async def analyze():
    """Run complete analysis"""
    global current_data, analysis_running, last_update
    
    if analysis_running:
        raise HTTPException(status_code=409, detail="Analysis already running")
    
    try:
        analysis_running = True
        
        # Run analysis in thread to avoid blocking
        def run_analysis_thread():
            global current_data, last_update
            try:
                current_data = analysis_service.run_analysis()
                last_update = datetime.now()
                return True
            except Exception as e:
                import traceback
                print(f"Analysis thread error: {e}")
                print(f"Full traceback: {traceback.format_exc()}")
                return False
        
        # For now, run synchronously (can be made async later)
        success = run_analysis_thread()
        
        if success:
            return {"success": True, "message": "Analysis completed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Analysis failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        analysis_running = False

@app.get("/api/data")
async def get_data():
    """Get current chart data"""
    global current_data
    
    if current_data is None:
        # Try to load existing data
        current_data = analysis_service.get_existing_data()
        
        if current_data is None:
            raise HTTPException(status_code=404, detail="No analysis data available. Please run analysis first.")
    
    return current_data

@app.get("/api/market-cap")
async def get_market_cap_data():
    """Get market cap top 20 stocks price changes"""
    try:
        chart_data = analysis_service.market_cap_analyzer.get_chart_data_json()
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch market cap data: {str(e)}")

@app.get("/api/status")
async def get_status():
    """Get current analysis status"""
    global analysis_running, last_update
    
    return {
        "running": analysis_running,
        "last_update": last_update.isoformat() if last_update else None
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Nikkei 225 Analysis Web Application")
    print("📊 Dashboard: http://localhost:8001")
    print("📡 API docs: http://localhost:8001/docs")
    print("\nPress Ctrl+C to stop the server")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)