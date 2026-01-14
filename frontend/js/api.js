/**
 * API.js - API Communication Module
 * Handles all communication with the backend API
 */

const API_BASE = '/api';

class APIClient {
    constructor() {
        this.baseUrl = API_BASE;
    }

    async analyze(ohlcData, gexData = null) {
        try {
            const payload = {
                ohlc_data: ohlcData,
                ...gexData
            };

            const response = await fetch(`${this.baseUrl}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Analysis error:', error);
            throw error;
        }
    }

    async calculateGEX(spotPrice, strikePrices, gammaValues, openInterest) {
        try {
            const response = await fetch(`${this.baseUrl}/calculator`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    spot_price: spotPrice,
                    strike_prices: strikePrices,
                    gamma_values: gammaValues,
                    open_interest: openInterest
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('GEX calculation error:', error);
            throw error;
        }
    }

    async detectPatterns(ohlcData) {
        try {
            const response = await fetch(`${this.baseUrl}/patterns`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ohlc_data: ohlcData
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Pattern detection error:', error);
            throw error;
        }
    }

    async analyzeRegime(ohlcData) {
        try {
            const response = await fetch(`${this.baseUrl}/regime`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ohlc_data: ohlcData
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Regime analysis error:', error);
            throw error;
        }
    }

    async generateSignals(ohlcData, gexData = {}) {
        try {
            const response = await fetch(`${this.baseUrl}/signals`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ohlc_data: ohlcData,
                    gex_data: gexData
                })
            });

            if (!response.ok) {
                throw new Error(`API error: ${response.statusText}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Signal generation error:', error);
            throw error;
        }
    }

    async healthCheck() {
        try {
            const response = await fetch('/api/health', {
                method: 'GET'
            });
            return response.ok;
        } catch (error) {
            console.error('Health check error:', error);
            return false;
        }
    }
}

// Create global API client instance
const api = new APIClient();
