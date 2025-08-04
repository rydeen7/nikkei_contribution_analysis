// Chart.js default configuration
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';

// Global chart instances
let industryChart = null;
let stockChart = null;
let marketCapChart = null;


// Create horizontal bar chart for contributions
function createContributionChart(ctx, data, title) {
    const config = {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: data.values.map(v => v >= 0 ? 'rgba(34, 197, 94, 0.8)' : 'rgba(239, 68, 68, 0.8)'),
                borderColor: data.values.map(v => v >= 0 ? 'rgb(34, 197, 94)' : 'rgb(239, 68, 68)'),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.parsed.x.toFixed(2) + ' 円';
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1);
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    };
    
    return new Chart(ctx, config);
}

// Create market cap price change chart
function createMarketCapChart(ctx, data) {
    console.log('Creating market cap chart with:', data);
    if (!data || !data.labels || !data.values || data.labels.length === 0) {
        console.error('Invalid market cap data format');
        return null;
    }
    
    // Log data details for debugging
    console.log('Labels count:', data.labels.length);
    console.log('Values count:', data.values.length);
    console.log('First few labels:', data.labels.slice(0, 3));
    console.log('First few values:', data.values.slice(0, 3));
    
    const config = {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: '前日比変動率 (%)',
                data: data.values,
                backgroundColor: data.values.map(v => v >= 0 ? 'rgba(59, 130, 246, 0.8)' : 'rgba(239, 68, 68, 0.8)'),
                borderColor: data.values.map(v => v >= 0 ? 'rgb(59, 130, 246)' : 'rgb(239, 68, 68)'),
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const index = context.dataIndex;
                            const code = data.codes[index];
                            return `${code}: ${context.parsed.x.toFixed(2)}%`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: true,
                        color: 'rgba(0, 0, 0, 0.05)'
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + '%';
                        }
                    }
                },
                y: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 12
                        }
                    }
                }
            }
        }
    };
    
    return new Chart(ctx, config);
}

// Update all charts with data
function updateCharts(data) {
    // Update industry contributions chart
    if (data.industry_contributions && data.industry_contributions.labels.length > 0) {
        const industryCtx = document.getElementById('industryChart').getContext('2d');
        if (industryChart) {
            industryChart.destroy();
        }
        industryChart = createContributionChart(industryCtx, data.industry_contributions, '業種別寄与度');
    }
    
    // Update stock contributions chart
    if (data.stock_contributions && data.stock_contributions.labels.length > 0) {
        const stockCtx = document.getElementById('stockChart').getContext('2d');
        if (stockChart) {
            stockChart.destroy();
        }
        stockChart = createContributionChart(stockCtx, data.stock_contributions, '個別銘柄寄与度');
    }
    
    // Update market cap chart if available
    if (data.market_cap_changes) {
        console.log('Updating market cap chart with data:', data.market_cap_changes);
        const marketCapCanvas = document.getElementById('marketCapChart');
        if (!marketCapCanvas) {
            console.error('Market cap canvas element not found');
            return;
        }
        const marketCapCtx = marketCapCanvas.getContext('2d');
        if (!marketCapCtx) {
            console.error('Failed to get 2d context for market cap chart');
            return;
        }
        
        if (marketCapChart) {
            marketCapChart.destroy();
        }
        marketCapChart = createMarketCapChart(marketCapCtx, data.market_cap_changes);
        
        if (marketCapChart) {
            console.log('Market cap chart created successfully');
        } else {
            console.error('Failed to create market cap chart');
        }
    } else {
        console.log('No market cap data available');
    }
    
    // Update last updated time
    if (data.last_updated) {
        document.getElementById('status').textContent = `最終更新: ${data.last_updated}`;
    }
}