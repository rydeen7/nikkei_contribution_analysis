// API communication functions

// Show loading state
function showLoading() {
    const containers = ['nikkeiChart', 'industryChart', 'stockChart', 'marketCapChart'];
    containers.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
        }
    });
    
    document.getElementById('status').textContent = '読み込み中...';
}

// Show error message
function showError(message) {
    const errorHtml = `<div class="error">エラー: ${message}</div>`;
    
    const containers = ['nikkeiChart', 'industryChart', 'stockChart', 'marketCapChart'];
    containers.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = errorHtml;
        }
    });
    
    document.getElementById('status').textContent = 'エラーが発生しました';
}

// Fetch chart data from API
async function fetchChartData() {
    try {
        const response = await fetch('/api/data');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('データ取得エラー:', error);
        throw error;
    }
}

// Fetch market cap data from API
async function fetchMarketCapData() {
    try {
        const response = await fetch('/api/market-cap');
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('時価総額データ取得エラー:', error);
        throw error;
    }
}

// Run full analysis
async function runAnalysis() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    
    // Disable buttons during analysis
    analyzeBtn.disabled = true;
    refreshBtn.disabled = true;
    analyzeBtn.textContent = '分析実行中...';
    
    showLoading();
    
    try {
        const response = await fetch('/api/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        
        if (result.success) {
            // Analysis completed successfully, refresh data
            await refreshData();
        } else {
            throw new Error(result.message || '分析に失敗しました');
        }
        
    } catch (error) {
        console.error('分析エラー:', error);
        showError(error.message);
    } finally {
        // Re-enable buttons
        analyzeBtn.disabled = false;
        refreshBtn.disabled = false;
        analyzeBtn.textContent = 'Run Analysis';
    }
}

// Refresh chart data
async function refreshData() {
    try {
        showLoading();
        
        // First try to get the data from the API which should already include market cap data
        const chartData = await fetchChartData();
        
        // If market cap data is not included, fetch it separately
        if (!chartData.market_cap_changes) {
            const marketCapData = await fetchMarketCapData();
            chartData.market_cap_changes = marketCapData;
        }
        
        console.log('Market cap data:', chartData.market_cap_changes);
        updateCharts(chartData);
        
        document.getElementById('status').textContent = `最終更新: ${new Date().toLocaleString('ja-JP')}`;
        
    } catch (error) {
        console.error('データ更新エラー:', error);
        showError(error.message);
    }
}

// Check if weekend/holiday and show appropriate message
function checkTradingDay() {
    const now = new Date();
    const day = now.getDay(); // 0 = Sunday, 6 = Saturday
    
    if (day === 0 || day === 6) {
        const infoHtml = '<div class="info">今日は休場日です。最新の取引日のデータを表示しています。</div>';
        document.querySelector('.container').insertAdjacentHTML('afterbegin', infoHtml);
    }
}