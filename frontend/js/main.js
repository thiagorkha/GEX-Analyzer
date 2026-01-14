/**
 * Main.js - Main Application Logic
 * Orchestrates the GEX Analyzer application
 */

class GexAnalyzerApp {
    constructor() {
        this.api = api;
        this.chartManager = chartManager;
        this.currentData = null;
        this.currentAnalysis = null;
        this.init();
    }

    async init() {
        this.setupEventListeners();
        this.chartManager.initializePriceChart('price-chart');
        this.chartManager.initializeGexChart('gex-chart');
        
        // Check API health
        const healthy = await this.api.healthCheck();
        if (!healthy) {
            this.showError('Unable to connect to API server');
        }
    }

    setupEventListeners() {
        // Analyze button
        document.getElementById('analyze-btn').addEventListener('click', () => this.analyzeData());

        // Load example button
        document.getElementById('load-example-btn').addEventListener('click', () => this.loadExampleData());

        // Tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.switchTab(e.target.dataset.tab));
        });

        // Auto-focus on error/success messages
        const errorMsg = document.getElementById('error-message');
        const successMsg = document.getElementById('success-message');
        
        if (errorMsg) errorMsg.addEventListener('click', () => this.clearError());
        if (successMsg) successMsg.addEventListener('click', () => this.clearSuccess());
    }

    async analyzeData() {
        try {
            const dataInput = document.getElementById('data-input').value;
            const gexInput = document.getElementById('gex-data').value;

            if (!dataInput.trim()) {
                this.showError('Please enter OHLC data');
                return;
            }

            // Show loading state
            this.setLoading(true);

            // Parse input data
            let ohlcData;
            try {
                ohlcData = JSON.parse(dataInput);
            } catch (e) {
                this.showError('Invalid JSON format for OHLC data');
                this.setLoading(false);
                return;
            }

            let gexData = {};
            if (gexInput.trim()) {
                try {
                    gexData = JSON.parse(gexInput);
                } catch (e) {
                    this.showError('Invalid JSON format for GEX data');
                    this.setLoading(false);
                    return;
                }
            }

            // Call API
            const result = await this.api.analyze(ohlcData, gexData);

            if (result.error) {
                this.showError(result.error);
                this.setLoading(false);
                return;
            }

            // Store results
            this.currentData = ohlcData;
            this.currentAnalysis = result;

            // Update UI
            this.displayResults(result);
            this.updateCharts(ohlcData, result);

            this.showSuccess('Analysis completed successfully');
            this.setLoading(false);

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError(`Analysis failed: ${error.message}`);
            this.setLoading(false);
        }
    }

    async loadExampleData() {
        try {
            const response = await fetch('assets/example_data.json');
            const data = await response.json();

            document.getElementById('data-input').value = JSON.stringify(data.ohlc, null, 2);
            if (data.gex) {
                document.getElementById('gex-data').value = JSON.stringify(data.gex, null, 2);
            }

            this.showSuccess('Example data loaded');
        } catch (error) {
            this.showError('Could not load example data');
        }
    }

    displayResults(analysis) {
        // Update summary cards
        if (analysis.summary) {
            document.getElementById('current-price').textContent = 
                analysis.summary.current_price.toFixed(2);
            document.getElementById('volume').textContent = 
                (analysis.summary.volume_24h / 1e6).toFixed(2) + 'M';
        }

        // Update GEX analysis
        if (analysis.gex_analysis) {
            const gex = analysis.gex_analysis;
            document.getElementById('net-gex').textContent = gex.net_gex.toFixed(2);
            document.getElementById('gex-interpretation').textContent = gex.interpretation;
        }

        // Update regimes
        if (analysis.regimes && analysis.regimes.length > 0) {
            document.getElementById('regime').textContent = analysis.regimes[0].type.toUpperCase();
        }

        // Display patterns
        this.displayPatterns(analysis.patterns || []);

        // Display regimes
        this.displayRegimes(analysis.regimes || []);

        // Display signals
        this.displaySignals(analysis.signals || []);

        // Display trading signals
        this.displayTradingSignals(analysis.signals || []);
    }

    displayPatterns(patterns) {
        const container = document.getElementById('patterns-list');
        
        if (!patterns || patterns.length === 0) {
            container.innerHTML = '<p>No patterns detected</p>';
            return;
        }

        container.innerHTML = patterns.map(pattern => `
            <div class="result-item">
                <h4>${pattern.description}</h4>
                <p><strong>Type:</strong> ${pattern.type}</p>
                <p><strong>Strength:</strong> ${pattern.strength.toFixed(1)}%</p>
                <p><strong>Confidence:</strong> ${(pattern.confidence * 100).toFixed(1)}%</p>
                <span class="badge ${pattern.type}">${pattern.type}</span>
            </div>
        `).join('');
    }

    displayRegimes(regimes) {
        const container = document.getElementById('regimes-list');
        
        if (!regimes || regimes.length === 0) {
            container.innerHTML = '<p>No regimes identified</p>';
            return;
        }

        container.innerHTML = regimes.map(regime => `
            <div class="result-item">
                <h4>${regime.type.toUpperCase()}</h4>
                <p><strong>Confidence:</strong> ${(regime.confidence * 100).toFixed(1)}%</p>
                <p><strong>Avg Return:</strong> ${(regime.characteristics.avg_return * 100).toFixed(3)}%</p>
                <p><strong>Volatility:</strong> ${(regime.characteristics.volatility * 100).toFixed(3)}%</p>
            </div>
        `).join('');
    }

    displaySignals(signals) {
        const container = document.getElementById('signals-list');
        
        if (!signals || signals.length === 0) {
            container.innerHTML = '<p>No signals generated</p>';
            return;
        }

        container.innerHTML = signals.map(signal => `
            <div class="result-item">
                <h4>${signal.reason}</h4>
                <p><strong>Type:</strong> ${signal.type}</p>
                <p><strong>Confidence:</strong> ${(signal.confidence * 100).toFixed(1)}%</p>
                <p><strong>Entry:</strong> ${signal.entry_price.toFixed(2)}</p>
                <p><strong>TP:</strong> ${signal.take_profit.toFixed(2)}</p>
                <p><strong>SL:</strong> ${signal.stop_loss.toFixed(2)}</p>
                <span class="badge ${signal.type}">${signal.type}</span>
            </div>
        `).join('');
    }

    displayTradingSignals(signals) {
        const container = document.getElementById('trading-signals');
        
        if (!signals || signals.length === 0) {
            container.innerHTML = '<p>No trading signals generated</p>';
            return;
        }

        container.innerHTML = signals.map(signal => `
            <div class="signal-card ${signal.type}">
                <h3>
                    <span class="signal-type ${signal.type}">${signal.type.toUpperCase()}</span>
                </h3>
                <div class="signal-details">
                    <div class="signal-detail">
                        <label>Reason</label>
                        <value>${signal.reason}</value>
                    </div>
                    <div class="signal-detail">
                        <label>Confidence</label>
                        <value>${(signal.confidence * 100).toFixed(1)}%</value>
                    </div>
                    <div class="signal-detail">
                        <label>Entry Price</label>
                        <value>${signal.entry_price.toFixed(2)}</value>
                    </div>
                    <div class="signal-detail">
                        <label>Take Profit</label>
                        <value>${signal.take_profit.toFixed(2)}</value>
                    </div>
                    <div class="signal-detail">
                        <label>Stop Loss</label>
                        <value>${signal.stop_loss.toFixed(2)}</value>
                    </div>
                </div>
            </div>
        `).join('');
    }

    updateCharts(ohlcData, analysis) {
        // Update price chart
        if (ohlcData && ohlcData.length > 0) {
            this.chartManager.updatePriceChart(ohlcData);
        }

        // Update GEX chart if available
        if (analysis.gex_analysis) {
            // Note: This would need actual strike prices and gamma exposure
            // For now, we'll create synthetic data for demonstration
            const strikeCount = 10;
            const currentPrice = analysis.summary.current_price;
            const strikes = Array.from({length: strikeCount}, (_, i) => 
                currentPrice * (0.9 + i * 0.02)
            );
            
            // Synthetic gamma exposure
            const gammaExposure = strikes.map(strike => {
                const distance = Math.abs(strike - currentPrice) / currentPrice;
                return Math.sin(distance * Math.PI) * 100;
            });

            this.chartManager.updateGexChart(strikes, gammaExposure);
        }
    }

    switchTab(tabId) {
        // Hide all tabs
        document.querySelectorAll('.tab-content').forEach(tab => {
            tab.classList.remove('active');
        });

        // Remove active class from all buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });

        // Show selected tab
        const selectedTab = document.getElementById(tabId);
        if (selectedTab) {
            selectedTab.classList.add('active');
        }

        // Add active class to clicked button
        event.target.classList.add('active');
    }

    setLoading(isLoading) {
        const btn = document.getElementById('analyze-btn');
        if (isLoading) {
            btn.disabled = true;
            btn.textContent = 'Analyzing...';
        } else {
            btn.disabled = false;
            btn.textContent = 'Analyze';
        }
    }

    showError(message) {
        const errorEl = document.getElementById('error-message');
        errorEl.textContent = message;
        errorEl.classList.add('show');
        setTimeout(() => this.clearError(), 5000);
    }

    showSuccess(message) {
        const successEl = document.getElementById('success-message');
        successEl.textContent = message;
        successEl.classList.add('show');
        setTimeout(() => this.clearSuccess(), 3000);
    }

    clearError() {
        document.getElementById('error-message').classList.remove('show');
    }

    clearSuccess() {
        document.getElementById('success-message').classList.remove('show');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new GexAnalyzerApp();
});
