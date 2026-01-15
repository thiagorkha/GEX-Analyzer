/**
 * Excel Parser for GEX Analyzer
 * Parses Excel files with options data (ticker, tipo, strike, gamma, OI)
 */

class ExcelParser {
    constructor() {
        this.fileInput = document.getElementById('file-input');
        this.uploadArea = document.getElementById('file-upload-area');
        this.fileStatus = document.getElementById('file-status');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Click to upload
        this.uploadArea.addEventListener('click', () => this.fileInput.click());

        // File input change
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.fileInput.files = files;
                this.handleFileSelect({ target: { files } });
            }
        });
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length === 0) return;

        const file = files[0];
        const fileName = file.name.toLowerCase();

        if (!fileName.match(/\.(xlsx|xls|csv)$/)) {
            this.showError('Por favor, selecione um arquivo Excel (.xlsx, .xls) ou CSV (.csv)');
            return;
        }

        this.parseFile(file)
            .then(data => this.handleParsedData(data))
            .catch(error => this.showError(`Erro ao processar arquivo: ${error.message}`));
    }

    parseFile(file) {
        return new Promise((resolve, reject) => {
            const fileName = file.name.toLowerCase();

            if (fileName.endsWith('.csv')) {
                this.parseCSV(file, resolve, reject);
            } else {
                this.parseExcel(file, resolve, reject);
            }
        });
    }

    parseExcel(file, resolve, reject) {
        const reader = new FileReader();

        reader.onload = (e) => {
            try {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array' });
                const sheet = workbook.Sheets[workbook.SheetNames[0]];
                const jsonData = XLSX.utils.sheet_to_json(sheet);

                const parsed = this.validateAndFormatData(jsonData);
                resolve(parsed);
            } catch (error) {
                reject(error);
            }
        };

        reader.onerror = () => reject(new Error('Erro ao ler arquivo'));
        reader.readAsArrayBuffer(file);
    }

    parseCSV(file, resolve, reject) {
        const reader = new FileReader();

        reader.onload = (e) => {
            try {
                const csv = e.target.result;
                const lines = csv.split('\n').filter(line => line.trim());
                
                if (lines.length < 2) {
                    throw new Error('Arquivo CSV vazio ou com apenas cabeçalho');
                }

                // Parse header
                const headers = lines[0]
                    .split(',')
                    .map(h => h.trim().toLowerCase());

                // Parse rows
                const jsonData = [];
                for (let i = 1; i < lines.length; i++) {
                    const values = lines[i].split(',').map(v => v.trim());
                    const row = {};
                    headers.forEach((header, index) => {
                        row[header] = values[index] || '';
                    });
                    jsonData.push(row);
                }

                const parsed = this.validateAndFormatData(jsonData);
                resolve(parsed);
            } catch (error) {
                reject(error);
            }
        };

        reader.onerror = () => reject(new Error('Erro ao ler arquivo CSV'));
        reader.readAsText(file);
    }

    validateAndFormatData(jsonData) {
        if (jsonData.length === 0) {
            throw new Error('Arquivo não contém dados');
        }

        // Map flexible column names
        const columnMap = {
            'ticker': ['ticker', 'symbol', 'ativo'],
            'tipo': ['tipo', 'type', 'option_type', 'optiontype'],
            'strike': ['strike', 'strike_price', 'strikeprice'],
            'gamma': ['gamma', 'gamma_value'],
            'oi': ['oi', 'open_interest', 'openinterest', 'volume']
        };

        const options = [];

        for (const row of jsonData) {
            const option = {};
            let foundRequiredFields = 0;

            for (const [key, aliases] of Object.entries(columnMap)) {
                const rowKey = Object.keys(row).find(k => 
                    aliases.includes(k.toLowerCase())
                );

                if (rowKey) {
                    let value = row[rowKey];

                    // Parse numeric fields
                    if (['strike', 'gamma', 'oi'].includes(key)) {
                        value = parseFloat(value);
                        if (isNaN(value)) {
                            throw new Error(`Valor inválido para ${key}: ${row[rowKey]}`);
                        }
                    }

                    option[key] = value;
                    foundRequiredFields++;
                }
            }

            if (foundRequiredFields >= 5) {
                options.push(option);
            }
        }

        if (options.length === 0) {
            throw new Error('Nenhuma linha válida encontrada com as colunas esperadas');
        }

        console.log('✅ Excel Parser: Carregado com sucesso', options);
        return options;
    }

    handleParsedData(options) {
        console.log('✅ Excel Parser - Dados parseados:', options);
        this.fileStatus.textContent = `✅ ${options.length} opções carregadas com sucesso`;
        this.fileStatus.style.color = '#10b981';

        // Store in window for access from main.js
        window.uploadedOptions = options;
        console.log('📦 window.uploadedOptions atualizado:', window.uploadedOptions);

        // Enable analyze button
        document.getElementById('analyze-btn').disabled = false;
    }

    showError(message) {
        console.error('❌ Excel Parser Error:', message);
        this.fileStatus.textContent = `❌ ${message}`;
        this.fileStatus.style.color = '#ef4444';
        this.fileInput.value = '';
        window.uploadedOptions = null;
        document.getElementById('analyze-btn').disabled = true;
    }

    getUploadedOptions() {
        const options = window.uploadedOptions || [];
        console.log('📊 getUploadedOptions() retornando:', options.length, 'opções');
        return options;
    }
}

// Initialize parser
document.addEventListener('DOMContentLoaded', () => {
    console.log('🔧 ExcelParser: Inicializando...');
    try {
        window.excelParser = new ExcelParser();
        console.log('✅ ExcelParser: Inicializado com sucesso');
    } catch (error) {
        console.error('❌ ExcelParser: Erro ao inicializar:', error);
    }
});
