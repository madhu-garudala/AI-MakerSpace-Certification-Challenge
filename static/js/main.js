// Main JavaScript for KidSafe Food Analyzer

document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const configureBtn = document.getElementById('configure-btn');
    const configStatus = document.getElementById('config-status');
    const selectionCard = document.getElementById('selection-card');
    const resultsCard = document.getElementById('results-card');
    const cerealSelect = document.getElementById('cereal-select');
    const selectedInfo = document.getElementById('selected-info');
    const selectedCerealName = document.getElementById('selected-cereal-name');
    const analyzeBtn = document.getElementById('analyze-btn');
    const analysisLoading = document.getElementById('analysis-loading');
    const analysisResults = document.getElementById('analysis-results');
    const resultCerealName = document.getElementById('result-cereal-name');
    
    // API Keys
    const openaiKeyInput = document.getElementById('openai-key');
    const langsmithKeyInput = document.getElementById('langsmith-key');
    const cohereKeyInput = document.getElementById('cohere-key');
    const tavilyKeyInput = document.getElementById('tavily-key');
    const retrievalStrategySelect = document.getElementById('retrieval-strategy');
    
    // State
    let isSystemInitialized = false;
    let currentIngredients = '';
    
    // Check system status on load
    checkSystemStatus();
    
    // Configure button click handler
    configureBtn.addEventListener('click', async function() {
        const openaiKey = openaiKeyInput.value.trim();
        const langsmithKey = langsmithKeyInput.value.trim();
        const cohereKey = cohereKeyInput.value.trim();
        const tavilyKey = tavilyKeyInput.value.trim();
        const retrievalStrategy = retrievalStrategySelect.value;
        
        if (!openaiKey || !langsmithKey) {
            showStatus('Please provide both OpenAI and LangSmith API keys', 'error');
            return;
        }
        
        // Disable button and show loading
        configureBtn.disabled = true;
        configureBtn.innerHTML = '<span class="spinner" style="width: 20px; height: 20px; border-width: 2px;"></span> Initializing...';
        
        try {
            const response = await fetch('/api/configure', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    openai_api_key: openaiKey,
                    langsmith_api_key: langsmithKey,
                    cohere_api_key: cohereKey,
                    tavily_api_key: tavilyKey,
                    retrieval_strategy: retrievalStrategy
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showStatus(data.message, 'success');
                isSystemInitialized = true;
                
                // Enable selection card
                selectionCard.style.opacity = '1';
                selectionCard.style.pointerEvents = 'auto';
                
                // Update button
                configureBtn.innerHTML = '✓ System Initialized';
                configureBtn.style.background = 'linear-gradient(135deg, #10B981, #059669)';
            } else {
                showStatus('Error: ' + data.error, 'error');
                configureBtn.disabled = false;
                configureBtn.innerHTML = 'Initialize System <span class="btn-icon">🚀</span>';
            }
        } catch (error) {
            showStatus('Network error: ' + error.message, 'error');
            configureBtn.disabled = false;
            configureBtn.innerHTML = 'Initialize System <span class="btn-icon">🚀</span>';
        }
    });
    
    // Cereal selection handler
    cerealSelect.addEventListener('change', function() {
        const selectedValue = this.value;
        const selectedOption = this.options[this.selectedIndex];
        
        if (selectedValue) {
            currentIngredients = selectedOption.dataset.ingredients || '';
            selectedInfo.style.display = 'block';
            selectedCerealName.textContent = selectedValue;
            
            // Hide results from previous analysis
            resultsCard.style.display = 'none';
        } else {
            selectedInfo.style.display = 'none';
            currentIngredients = '';
        }
    });
    
    // Analyze button handler
    analyzeBtn.addEventListener('click', async function() {
        if (!isSystemInitialized) {
            showNotification('Please configure API keys first!', 'error');
            return;
        }
        
        const selectedCereal = cerealSelect.value;
        
        if (!selectedCereal || !currentIngredients) {
            showNotification('Please select a cereal first!', 'error');
            return;
        }
        
        // Show loading
        analysisLoading.style.display = 'block';
        analyzeBtn.disabled = true;
        resultsCard.style.display = 'none';
        
        try {
            const response = await fetch('/api/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cereal_name: selectedCereal,
                    ingredients: currentIngredients
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Display results
                displayAnalysis(data.cereal_name, data.analysis);
                showNotification('Analysis complete!', 'success');
            } else {
                showNotification('Error: ' + data.error, 'error');
            }
        } catch (error) {
            showNotification('Network error: ' + error.message, 'error');
        } finally {
            // Hide loading
            analysisLoading.style.display = 'none';
            analyzeBtn.disabled = false;
        }
    });
    
    // Helper function to check system status
    async function checkSystemStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (data.initialized) {
                isSystemInitialized = true;
                selectionCard.style.opacity = '1';
                selectionCard.style.pointerEvents = 'auto';
                configureBtn.innerHTML = '✓ System Initialized';
                configureBtn.style.background = 'linear-gradient(135deg, #10B981, #059669)';
                configureBtn.disabled = true;
            }
        } catch (error) {
            console.log('Could not check system status:', error);
        }
    }
    
    // Helper function to display analysis
    function displayAnalysis(cerealName, analysis) {
        resultCerealName.textContent = cerealName;
        
        // Convert markdown-style formatting to HTML
        let htmlContent = analysis
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\n### (.*?)\n/g, '<h3>$1</h3>')
            .replace(/\n## (.*?)\n/g, '<h3>$1</h3>')
            .replace(/\n# (.*?)\n/g, '<h3>$1</h3>')
            .replace(/\n\n/g, '</p><p>')
            .replace(/\n- /g, '</li><li>')
            .replace(/<li>/i, '<ul><li>')
            .replace(/(<li>.*)/i, '$1</ul>');
        
        // Wrap in paragraph tags if not already wrapped
        if (!htmlContent.startsWith('<')) {
            htmlContent = '<p>' + htmlContent + '</p>';
        }
        
        analysisResults.innerHTML = htmlContent;
        resultsCard.style.display = 'block';
        
        // Scroll to results
        resultsCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    
    // Helper function to show status message
    function showStatus(message, type) {
        configStatus.textContent = message;
        configStatus.className = `status-message show ${type}`;
        
        if (type === 'success') {
            setTimeout(() => {
                configStatus.classList.remove('show');
            }, 5000);
        }
    }
    
    // Helper function to show notification
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        const bgColor = {
            'success': '#10B981',
            'error': '#EF4444',
            'info': '#3B82F6'
        }[type] || '#3B82F6';
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            background: ${bgColor};
            color: white;
            border-radius: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            z-index: 1000;
            animation: slideIn 0.3s ease-out;
            font-weight: 500;
            font-family: 'Poppins', sans-serif;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
    
    // Add animation styles
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOut {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(400px);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
});
