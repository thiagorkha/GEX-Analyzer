/**
 * Chart.js - Chart Management Module
 * Handles all chart creation and updates
 */

class ChartManager {
    constructor() {
        this.charts = {};
        this.chartConfig = {
            price: null,
            gex: null
        };
    }

    initializePriceChart(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        this.charts.price = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Close Price',
                        data: [],
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 0,
                        pointHoverRadius: 6
                    },
                    {
                        label: 'High',
                        data: [],
                        borderColor: '#10b981',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    },
                    {
                        label: 'Low',
                        data: [],
                        borderColor: '#ef4444',
                        borderWidth: 1,
                        borderDash: [5, 5],
                        fill: false,
                        pointRadius: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'Price Analysis'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        title: {
                            display: true,
                            text: 'Price'
                        }
                    },
                    x: {
                        display: true
                    }
                }
            }
        });
    }

    initializeGexChart(canvasId) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        this.charts.gex = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Gamma Exposure',
                        data: [],
                        backgroundColor: [],
                        borderRadius: 4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true
                    },
                    title: {
                        display: true,
                        text: 'Gamma Exposure by Strike'
                    }
                },
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: 'GEX Value'
                        }
                    }
                }
            }
        });
    }

    updatePriceChart(data) {
        if (!this.charts.price || !data) return;

        const labels = data.map((d, i) => i.toString());
        const closes = data.map(d => parseFloat(d.close));
        const highs = data.map(d => parseFloat(d.high));
        const lows = data.map(d => parseFloat(d.low));

        this.charts.price.data.labels = labels;
        this.charts.price.data.datasets[0].data = closes;
        this.charts.price.data.datasets[1].data = highs;
        this.charts.price.data.datasets[2].data = lows;
        this.charts.price.update();
    }

    updateGexChart(strikes, gammaExposure) {
        if (!this.charts.gex || !strikes || !gammaExposure) return;

        const colors = gammaExposure.map(ge => 
            ge > 0 ? 'rgba(16, 185, 129, 0.7)' : 'rgba(239, 68, 68, 0.7)'
        );

        this.charts.gex.data.labels = strikes.map(s => s.toFixed(0));
        this.charts.gex.data.datasets[0].data = gammaExposure;
        this.charts.gex.data.datasets[0].backgroundColor = colors;
        this.charts.gex.update();
    }

    clearCharts() {
        Object.keys(this.charts).forEach(key => {
            if (this.charts[key]) {
                this.charts[key].destroy();
                this.charts[key] = null;
            }
        });
    }
}

// Create global chart manager instance
const chartManager = new ChartManager();
