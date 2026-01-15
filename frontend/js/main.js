/**
 * GEX Analyzer - Main Application Logic
 */

class GEXAnalyzerApp {
    constructor() {
        console.log('🔧 GEXAnalyzerApp construtor iniciando...');
        this.currentPrice = null;
        this.expirationDate = null;
        this.options = [];
        this.analysisResults = null;

        this.initElements();
        console.log('✅ Elementos inicializados');
        
        this.setupEventListeners();
        console.log('✅ Event listeners configurados');
        
        this.setDefaultExpirationDate();
        console.log('✅ Data padrão definida');
    }

    initElements() {
        console.log('🔍 Procurando elementos do DOM...');
        this.priceInput = document.getElementById('current-price');
        console.log('   ✓ current-price:', !!this.priceInput);
        
        this.expirationInput = document.getElementById('expiration-date');
        console.log('   ✓ expiration-date:', !!this.expirationInput);
        
        this.analyzeBtn = document.getElementById('analyze-btn');
        console.log('   ✓ analyze-btn:', !!this.analyzeBtn);
        
        this.loadExampleBtn = document.getElementById('load-example-btn');
        console.log('   ✓ load-example-btn:', !!this.loadExampleBtn);

        this.errorMsg = document.getElementById('error-message');
        console.log('   ✓ error-message:', !!this.errorMsg);
        
        this.successMsg = document.getElementById('success-message');
        console.log('   ✓ success-message:', !!this.successMsg);
        
        this.infoMsg = document.getElementById('info-message');
        console.log('   ✓ info-message:', !!this.infoMsg);
        
        this.loadingSpinner = document.getElementById('loading');
        console.log('   ✓ loading:', !!this.loadingSpinner);

        this.dashboardSection = document.getElementById('dashboard');
        console.log('   ✓ dashboard:', !!this.dashboardSection);
        
        this.resultsSection = document.getElementById('results');
        console.log('   ✓ results:', !!this.resultsSection);
    }

    setupEventListeners() {
        console.log('🎯 Configurando event listeners...');
        
        if (!this.analyzeBtn) {
            console.error('❌ analyze-btn não encontrado!');
        } else {
            console.log('   Adicionando listener ao analyze-btn');
            this.analyzeBtn.addEventListener('click', (e) => {
                console.log('🔔 Analyze button CLICADO!', e);
                this.handleAnalyze();
            });
        }
        
        if (!this.loadExampleBtn) {
            console.error('❌ load-example-btn não encontrado!');
        } else {
            console.log('   Adicionando listener ao load-example-btn');
            this.loadExampleBtn.addEventListener('click', () => {
                console.log('🔔 Load example button CLICADO!');
                this.loadExample();
            });
        }
        
        // Debug button
        const debugBtn = document.getElementById('debug-btn');
        if (!debugBtn) {
            console.warn('⚠️ debug-btn não encontrado');
        } else {
            console.log('   Adicionando listener ao debug-btn');
            debugBtn.addEventListener('click', () => {
                console.log('🔔 Debug button CLICADO!');
                this.showDebugInfo();
            });
        }
        
        console.log('✅ Event listeners configurados com sucesso');
    }

    showDebugInfo() {
        console.clear();
        console.log('========== DEBUG INFO ==========');
        console.log('Parser inicializado:', !!window.excelParser);
        console.log('Opções carregadas:', window.uploadedOptions?.length || 0, window.uploadedOptions);
        console.log('Preço atual:', this.priceInput.value);
        console.log('Data de expiração:', this.expirationInput.value);
        console.log('==============================');
        alert('✅ Verifique o console do navegador (F12) para ver informações de debug!');
    }

    setDefaultExpirationDate() {
        // Set to next Friday
        const today = new Date();
        const daysUntilFriday = (5 - today.getDay() + 7) % 7 || 7;
        const nextFriday = new Date(today.setDate(today.getDate() + daysUntilFriday));
        this.expirationInput.valueAsDate = nextFriday;
    }

    showError(message) {
        this.errorMsg.textContent = message;
        this.errorMsg.classList.remove('hidden');
        this.successMsg.classList.add('hidden');
        this.infoMsg.classList.add('hidden');
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showSuccess(message) {
        this.successMsg.textContent = message;
        this.successMsg.classList.remove('hidden');
        this.errorMsg.classList.add('hidden');
        this.infoMsg.classList.add('hidden');
    }

    showInfo(message) {
        this.infoMsg.textContent = message;
        this.infoMsg.classList.remove('hidden');
        this.errorMsg.classList.add('hidden');
        this.successMsg.classList.add('hidden');
    }

    showLoading(show = true) {
        if (show) {
            this.loadingSpinner.classList.remove('hidden');
            this.analyzeBtn.disabled = true;
        } else {
            this.loadingSpinner.classList.add('hidden');
            this.analyzeBtn.disabled = false;
        }
    }

    async handleAnalyze() {
        try {
            console.log('🔍 Iniciando análise...');
            
            this.currentPrice = parseFloat(this.priceInput.value);
            this.expirationDate = this.expirationInput.value;

            // Validate inputs
            if (!this.currentPrice || this.currentPrice <= 0) {
                this.showError('Por favor, insira um preço válido');
                console.error('❌ Preço inválido:', this.currentPrice);
                return;
            }

            if (!this.expirationDate) {
                this.showError('Por favor, selecione uma data de expiração');
                console.error('❌ Data não selecionada');
                return;
            }

            // Get uploaded options
            this.options = window.excelParser?.getUploadedOptions() || [];
            console.log('📊 Opções carregadas:', this.options.length, this.options);
            
            if (this.options.length === 0) {
                this.showError('Por favor, faça upload de um arquivo com dados das opções');
                console.error('❌ Nenhuma opção carregada');
                return;
            }

            this.showLoading(true);
            this.showInfo('Analisando dados... Aguarde.');

            console.log('📤 Enviando para API:', {
                current_price: this.currentPrice,
                expiration_date: this.expirationDate,
                options: this.options
            });

            // Call API
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    current_price: this.currentPrice,
                    expiration_date: this.expirationDate,
                    options: this.options
                })
            });

            console.log('📥 Resposta da API:', response.status, response.statusText);

            if (!response.ok) {
                const errorData = await response.json();
                console.error('❌ Erro da API:', errorData);
                throw new Error(errorData.error || 'Erro na análise');
            }

            const result = await response.json();
            console.log('✅ Análise completa:', result);
            
            this.analysisResults = result;

            this.showLoading(false);
            this.showSuccess(`✅ Análise completa! ${result.strikes.length} strikes analisados.`);
            this.displayResults(result);

        } catch (error) {
            this.showLoading(false);
            console.error('❌ Erro completo:', error);
            this.showError(`Erro: ${error.message}`);
        }
    }

    displayResults(result) {
        try {
            console.log('🎨 Iniciando displayResults com:', result);
            
            // Show sections
            this.dashboardSection.classList.remove('hidden');
            this.resultsSection.classList.remove('hidden');

            // Update dashboard cards
            document.getElementById('display-price').textContent = this.currentPrice.toFixed(2);
            document.getElementById('total-gex').textContent = result.total_gex.toFixed(0);
            document.getElementById('gex-regime').textContent = result.regime || 'Neutral';
            document.getElementById('walls-count').textContent = result.patterns?.walls?.length || 0;

            // Pin risk level
            const pinRiskElement = document.getElementById('pin-risk');
            if (result.patterns?.pins?.length > 0) {
                pinRiskElement.textContent = 'ALTO';
                pinRiskElement.className = 'value badge badge-danger';
            } else {
                pinRiskElement.textContent = 'BAIXO';
                pinRiskElement.className = 'value badge badge-success';
            }

            // Populate results table
            this.populateResultsTable(result.strikes);

            // Create charts
            this.createGexChart(result.strikes);
            this.createGammaChart(result.strikes);

            // Display patterns
            this.displayPatterns(result.patterns);

            // Display signals
            this.displaySignals(result.strategies);

            // Scroll to dashboard
            window.scrollTo({ top: this.dashboardSection.offsetTop - 100, behavior: 'smooth' });
            
            console.log('✅ displayResults completado com sucesso');
        } catch (error) {
            console.error('❌ Erro em displayResults:', error);
            this.showError(`Erro ao exibir resultados: ${error.message}`);
        }
    }

    populateResultsTable(strikes) {
        const tbody = document.getElementById('results-tbody');
        tbody.innerHTML = '';

        strikes.forEach(strike => {
            const row = document.createElement('tr');
            const statusClass = strike.gex > 0 ? 'badge-success' : 'badge-danger';
            const statusText = strike.gex > 0 ? 'Bullish' : 'Bearish';

            row.innerHTML = `
                <td><strong>${strike.strike.toFixed(2)}</strong></td>
                <td>${strike.type === 'CALL' ? '📈 CALL' : '📉 PUT'}</td>
                <td>${strike.gamma.toFixed(4)}</td>
                <td>${strike.oi.toLocaleString()}</td>
                <td><strong>${strike.gex.toFixed(0)}</strong></td>
                <td><span class="badge ${statusClass}">${statusText}</span></td>
            `;
            tbody.appendChild(row);
        });
    }

    createGexChart(strikes) {
        const containerDiv = document.getElementById('gex-chart').parentElement;
        const calls = strikes.filter(s => s.type === 'CALL');
        const puts = strikes.filter(s => s.type === 'PUT');

        const trace1 = {
            x: calls.map(s => s.strike),
            y: calls.map(s => s.gex),
            name: 'CALL GEX',
            type: 'bar',
            marker: { color: '#10b981' }
        };

        const trace2 = {
            x: puts.map(s => s.strike),
            y: puts.map(s => s.gex),
            name: 'PUT GEX',
            type: 'bar',
            marker: { color: '#ef4444' }
        };

        const layout = {
            title: 'GEX por Strike',
            xaxis: { title: 'Strike' },
            yaxis: { title: 'GEX' },
            barmode: 'group',
            responsive: true,
            margin: { b: 100 }
        };

        Plotly.newPlot(containerDiv, [trace1, trace2], layout, { responsive: true });
    }

    createGammaChart(strikes) {
        const containerDiv = document.getElementById('gamma-chart').parentElement;
        const calls = strikes.filter(s => s.type === 'CALL');
        const puts = strikes.filter(s => s.type === 'PUT');

        const trace1 = {
            x: calls.map(s => s.strike),
            y: calls.map(s => s.gamma),
            name: 'CALL Gamma',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#6366f1', width: 2 },
            marker: { size: 8 }
        };

        const trace2 = {
            x: puts.map(s => s.strike),
            y: puts.map(s => s.gamma),
            name: 'PUT Gamma',
            type: 'scatter',
            mode: 'lines+markers',
            line: { color: '#ec4899', width: 2 },
            marker: { size: 8 }
        };

        const layout = {
            title: 'Gamma por Strike',
            xaxis: { title: 'Strike' },
            yaxis: { title: 'Gamma' },
            responsive: true,
            margin: { b: 100 }
        };

        Plotly.newPlot(containerDiv, [trace1, trace2], layout, { responsive: true });
    }

    displayPatterns(patterns) {
        const container = document.getElementById('patterns-container');
        container.innerHTML = '';

        if (!patterns || Object.keys(patterns).length === 0) {
            container.innerHTML = '<p>Nenhum padrão detectado</p>';
            return;
        }

        // Walls
        if (patterns.walls && patterns.walls.length > 0) {
            patterns.walls.forEach(wall => {
                const card = this.createPatternCard(
                    '🧱 Gamma Wall',
                    `Strike: ${wall.strike.toFixed(2)}`,
                    `Força: ${wall.strength.toFixed(2)}`,
                    'info'
                );
                container.appendChild(card);
            });
        }

        // Flips
        if (patterns.flips && patterns.flips.length > 0) {
            patterns.flips.forEach(flip => {
                const card = this.createPatternCard(
                    '↔️ Gamma Flip',
                    `Strikes: ${flip.strike_call.toFixed(2)} / ${flip.strike_put.toFixed(2)}`,
                    `Intensidade: ${flip.strength.toFixed(2)}`,
                    'warning'
                );
                container.appendChild(card);
            });
        }

        // Pins
        if (patterns.pins && patterns.pins.length > 0) {
            patterns.pins.forEach(pin => {
                const card = this.createPatternCard(
                    '📌 Pin Risk',
                    `Strike: ${pin.strike.toFixed(2)}`,
                    `Risco Alto! Intensidade: ${pin.strength.toFixed(2)}`,
                    'danger'
                );
                container.appendChild(card);
            });
        }
    }

    createPatternCard(title, detail1, detail2, type) {
        const card = document.createElement('div');
        card.className = 'card';
        card.style.borderLeft = `4px solid var(--${type === 'danger' ? 'danger' : type === 'warning' ? 'warning' : 'info'})`;
        card.innerHTML = `
            <h4 style="margin-bottom: 0.5rem; color: var(--dark);">${title}</h4>
            <p style="font-size: 0.9rem; color: var(--text-light); margin: 0.25rem 0;">${detail1}</p>
            <p style="font-size: 0.9rem; color: var(--text); margin: 0.25rem 0; font-weight: 600;">${detail2}</p>
        `;
        return card;
    }

    displaySignals(strategies) {
        const container = document.getElementById('signals-container');
        container.innerHTML = '';

        if (!strategies || strategies.length === 0) {
            container.innerHTML = '<p>Nenhum sinal gerado</p>';
            return;
        }

        strategies.forEach(strategy => {
            const card = document.createElement('div');
            card.className = 'card';
            card.style.borderLeft = `4px solid ${strategy.direction === 'LONG' ? '#10b981' : '#ef4444'}`;

            const directionIcon = strategy.direction === 'LONG' ? '📈' : '📉';
            const confidenceColor = strategy.confidence > 0.7 ? '#10b981' : strategy.confidence > 0.5 ? '#f59e0b' : '#ef4444';

            card.innerHTML = `
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <h4 style="color: var(--dark); margin: 0;">${directionIcon} ${strategy.strategy_name}</h4>
                    <span class="badge" style="background: ${confidenceColor}20; color: ${confidenceColor}; border: 1px solid ${confidenceColor};">
                        ${(strategy.confidence * 100).toFixed(0)}%
                    </span>
                </div>
                <p style="color: var(--text-light); margin: 0.5rem 0; font-size: 0.9rem;">
                    <strong>Entrada:</strong> ${strategy.entry_price?.toFixed(2) || 'N/A'}
                </p>
                <p style="color: var(--text-light); margin: 0.5rem 0; font-size: 0.9rem;">
                    <strong>Target:</strong> ${strategy.target_price?.toFixed(2) || 'N/A'} | 
                    <strong>Stop:</strong> ${strategy.stop_loss?.toFixed(2) || 'N/A'}
                </p>
                <p style="color: var(--text-light); margin: 0.5rem 0; font-size: 0.9rem;">
                    ${strategy.description || ''}
                </p>
            `;

            container.appendChild(card);
        });
    }

    async loadExample() {
        try {
            this.showLoading(true);

            const response = await fetch('/api/examples');
            if (!response.ok) throw new Error('Erro ao carregar exemplo');

            const examples = await response.json();
            const example = examples[0]; // First example

            // Populate form
            this.priceInput.value = example.current_price;
            this.expirationInput.valueAsDate = new Date(example.expiration_date);

            // Set options
            window.uploadedOptions = example.options;
            document.getElementById('file-status').textContent = 
                `✅ ${example.options.length} opções do exemplo carregadas`;
            document.getElementById('file-status').style.color = '#10b981';

            this.showLoading(false);
            this.showSuccess('✅ Exemplo carregado! Clique em "Analisar GEX" para começar.');

        } catch (error) {
            this.showLoading(false);
            this.showError(`Erro ao carregar exemplo: ${error.message}`);
        }
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('✅ DOM Content Loaded - Iniciando GEXAnalyzerApp');
    window.app = new GEXAnalyzerApp();
    console.log('✅ GEXAnalyzerApp inicializado:', window.app);
    console.log('✅ ExcelParser disponível:', !!window.excelParser);
    console.log('✅ Elementos da UI:', {
        priceInput: !!window.app.priceInput,
        expirationInput: !!window.app.expirationInput,
        analyzeBtn: !!window.app.analyzeBtn,
        loadExampleBtn: !!window.app.loadExampleBtn
    });
});
