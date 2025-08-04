// Main application JavaScript

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Nikkei 225 Analysis Dashboard initialized');
    
    // Setup event listeners
    setupEventListeners();
    
    // Check if it's trading day
    checkTradingDay();
    
    // Load initial data
    refreshData();
});

// Setup all event listeners
function setupEventListeners() {
    // Analyze button
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (analyzeBtn) {
        analyzeBtn.addEventListener('click', runAnalysis);
    }
    
    // Refresh button
    const refreshBtn = document.getElementById('refreshBtn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', refreshData);
    }
    
    // Handle window resize for charts
    window.addEventListener('resize', handleResize);
}

// Handle window resize
function handleResize() {
    // Resize TradingView chart if it exists
    if (nikkeiChart && nikkeiChart.chart) {
        const container = document.getElementById('nikkeiChart');
        if (container) {
            nikkeiChart.chart.applyOptions({
                width: container.offsetWidth
            });
        }
    }
    
    // Chart.js charts automatically resize
}