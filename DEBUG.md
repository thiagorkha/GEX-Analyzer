# 🐛 GEX Analyzer - Guia de Debug

## Problema Reportado
"Eu carrego o arquivo em Excel com os dados, clico em analisar GEX e nada acontece"

## Solução: Debug Interativo

Existem **3 formas de debugar** o problema:

### 1️⃣ **Debug com Console do Navegador (RECOMENDADO)**

1. Abra o aplicativo: `http://localhost:5000` (ou seu site Render)
2. Pressione **F12** para abrir o Developer Tools
3. Vá para a aba **Console**
4. Veja se aparecem mensagens com ✅✓ ou ❌ durante:
   - Carregamento da página
   - Upload do Excel
   - Click no botão "Analisar GEX"

**Mensagens esperadas:**
```
✅ DOM Content Loaded
✅ GEXAnalyzerApp construtor iniciando...
✅ ExcelParser: Inicializado com sucesso
🔍 Iniciando análise...
📊 Opções carregadas: 5 opções
📤 Enviando para API: {...}
📥 Resposta da API: 200 OK
✅ Análise completa: {...}
```

Se alguma mensagem **NÃO APARECER**, isso indica onde o código está falhando.

---

### 2️⃣ **Debug com Página de Teste Interativa**

1. Abra: `http://localhost:5000/debug.html`
2. Use os botões para testar cada parte isoladamente:

**Passo 1: Verificação Inicial**
- Clique em **"Test Initialization"** - Verifica se app está carregado
- Clique em **"Test DOM Elements"** - Verifica se HTML elementos existem
- Clique em **"Test Event Listeners"** - Testa se botões respondem

**Passo 2: Entrada de Dados**
- Digite um preço no campo de input
- Clique em **"Set Test Data"** - Preenche dados de teste
- Clique em **"Load Test Options"** - Simula carregar arquivo Excel

**Passo 3: Teste de API**
- Clique em **"Simulate Analyze Click"** - Simula click no botão
- Clique em **"Test API Call Directly"** - Testa API diretamente

O console embutido mostra exatamente o que acontece em cada etapa.

---

### 3️⃣ **Teste Manual de API**

Abra seu navegador e acesse:

```
GET /api/health
```
Deve retornar: `{"status": "ok"}`

```
GET /api/examples
```
Deve retornar: Array com 4 exemplos

```
POST /api/analyze
```
Com payload:
```json
{
    "current_price": 100.0,
    "expiration_date": "2024-02-16",
    "options": [
        {"ticker": "SPY", "tipo": "CALL", "strike": 100.0, "gamma": 0.28, "oi": 12000},
        {"ticker": "SPY", "tipo": "PUT", "strike": 100.0, "gamma": 0.15, "oi": 4000}
    ]
}
```

---

## 🔍 Possíveis Causas & Soluções

### ❌ Erro: "JS Error in Console"
**Causa**: Erro de syntax ou missing variable
**Solução**: 
1. Abra F12 Console
2. Procure por linha vermelha (ERROR)
3. Note o nome do arquivo e linha
4. Reporte com a mensagem exata

### ❌ Erro: "API returns 404"
**Causa**: Servidor não iniciado ou rota errada
**Solução**:
1. Verifique se servidor está rodando: `python app.py`
2. Confira URL em `frontend/js/main.js` linha 135: `fetch('/api/analyze'...`
3. Verifique no `backend/api/routes.py` se rota `/api/analyze` existe

### ❌ Erro: "Excel não carrega"
**Causa**: Arquivo com formato errado ou XLSX library não carregou
**Solução**:
1. Verifique em F12 se há erro ao carregar `https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.min.js`
2. Tente criar arquivo Excel simples com colunas: `ticker, tipo, strike, gamma, OI`
3. Verifique se arquivo não tem linhas vazias

### ❌ Erro: "Botão não responde"
**Causa**: Event listener não configurado ou botão desabilitado
**Solução**:
1. Abra F12 Console
2. Digite: `document.getElementById('analyze-btn').click()`
3. Se funcionar, problema é o event listener
4. Se não funcionar, problema é a função `handleAnalyze()`

---

## 📝 Logs Importantes

Abra F12 e execute na console:

```javascript
// Ver estado da app
console.log('App:', window.app);
console.log('ExcelParser:', window.excelParser);
console.log('Opções carregadas:', window.uploadedOptions);

// Simular análise
window.app.handleAnalyze();

// Ver erro da API
window.app.handleAnalyze().catch(e => console.error(e));
```

---

## 📞 Reportar Problema

Se nenhuma solução funcionar, capture e reporte:

1. **Screenshot de F12 Console** (CRÍTICO)
   - Mostre todas as mensagens de erro/warning
   
2. **Arquivo Excel de Teste**
   - Envie o arquivo que está usando
   
3. **Resposta de `/api/examples`**
   - Acesse `http://localhost:5000/api/examples` no navegador
   - Screenshot da resposta

4. **Output de `network` tab em F12**
   - Vá para Network tab em F12
   - Faça click em "Analisar GEX"
   - Mostre a requisição `/api/analyze`
   - Mostre a resposta (request + response headers)

---

## 🚀 Links Úteis

- **Página Principal**: `http://localhost:5000/`
- **Debug Interativo**: `http://localhost:5000/debug.html`  
- **Teste API**: `http://localhost:5000/test_api.html`
- **Health Check**: `http://localhost:5000/api/health`
- **Exemplos**: `http://localhost:5000/api/examples`

---

## 💡 Pro Tips

1. **Vire console.log() seu amigo**
   - Toda ação importante está logada
   - Abra F12, recarregue página, veja os logs
   
2. **Use a página de Debug**
   - `/debug.html` é muito mais útil que debugar no main
   - Tem console integrada e testes isolados
   
3. **Network Tab é seu aliado**
   - F12 → Network → Faça a ação
   - Veja requisição/resposta exata
   - Verifique status code (200, 400, 500, etc)

4. **Teste passo a passo**
   - Não tente tudo junto
   - Test dados → Test Excel → Test Analyze
   - Identifique exatamente qual passo quebra

---

Boa sorte no debug! 🍀
