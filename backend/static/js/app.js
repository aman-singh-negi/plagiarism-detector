document.addEventListener('DOMContentLoaded', () => {
    // Theme management
    const themeToggle = document.getElementById('theme-toggle');
    const darkTheme = document.getElementById('dark-theme');
    let currentTheme = localStorage.getItem('theme') || 'light';
    
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        if (darkTheme) darkTheme.disabled = theme === 'light';
        if (themeToggle) {
            themeToggle.innerHTML = theme === 'dark' 
                ? '<i class="fas fa-sun"></i>' 
                : '<i class="fas fa-moon"></i>';
        }
        localStorage.setItem('theme', theme);
        console.log('Theme applied:', theme);
    }
    
    applyTheme(currentTheme);
    
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(currentTheme);
            console.log('Theme toggled:', currentTheme);
        });
    } else {
        console.log('Theme toggle button not found');
    }
    
    // Form submission
    const form = document.getElementById('upload-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            console.log('Analyze button clicked');
            
            const loadingOverlay = document.getElementById('loading-overlay');
            const submitBtn = form.querySelector('button[type="submit"]');
            const originalBtnText = submitBtn.innerHTML;
            
            loadingOverlay.style.display = 'flex';
            startLoadingProgress();
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
            
            try {
                const formData = new FormData(form);
                console.log('Sending /analyze request...');
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                console.log('Received response:', response.status);
                
                if (!response.ok) {
                    const errorText = await response.text();
                    console.log('Error response:', errorText);
                    throw new Error(errorText);
                }
                
                const data = await response.json();
                console.log('Response JSON:', data);
                if (data.error) throw new Error(data.error);
                
                displayResults(data);
            } catch (error) {
                showError(error.message);
                console.log('Analyze error:', error);
            } finally {
                finishLoadingProgress();
                setTimeout(() => {
                    loadingOverlay.style.display = 'none';
                }, 400); // Let user see 100% for a moment
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalBtnText;
            }
        });
    } else {
        console.log('Upload form not found');
    }
    
    function showError(message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
        `;
        
        document.querySelector('main').prepend(errorElement);
        
        setTimeout(() => {
            errorElement.classList.add('fade-out');
            setTimeout(() => errorElement.remove(), 500);
        }, 5000);
    }
    
    function showWarningPrompt(message) {
        let modal = document.getElementById('warning-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'warning-modal';
            modal.innerHTML = `
                <div class="warning-modal-backdrop"></div>
                <div class="warning-modal-content">
                    <div class="warning-modal-icon"><i class="fas fa-exclamation-triangle"></i></div>
                    <div class="warning-modal-message"></div>
                    <button class="warning-modal-close">OK</button>
                </div>
            `;
            document.body.appendChild(modal);
            modal.querySelector('.warning-modal-close').onclick = () => {
                modal.style.display = 'none';
            };
            modal.onclick = (e) => {
                if (e.target.classList.contains('warning-modal-backdrop')) {
                    modal.style.display = 'none';
                }
            };
        }
        modal.querySelector('.warning-modal-message').textContent = message;
        modal.style.display = 'flex';
    }
    
    function displayResults(data) {
        const resultsSection = document.getElementById('results');
        if (!resultsSection) return;
        
        resultsSection.classList.remove('hidden');
        resultsSection.style.display = 'block';
        
        if (data.results.warning) {
            showWarningPrompt(data.results.warning);
        }
        
        const scorePercent = Math.round(data.results.score * 100);
        
        resultsSection.innerHTML = `
            <div class="results-card">
                <div class="results-header">
                    <h2><i class="fas fa-chart-bar"></i> Analysis Results</h2>
                    <div class="result-meta">
                        <span><i class="fas fa-calendar-alt"></i> ${new Date(data.timestamp).toLocaleString()}</span>
                    </div>
                </div>
                
                <div class="similarity-score-container">
                    <div class="similarity-score">
                        <div class="score-value" id="score-value">0%</div>
                        <div class="score-label">Overall Similarity</div>
                    </div>
                    
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" id="progress-fill"></div>
                        </div>
                        <div class="progress-labels">
                            <span>0%</span>
                            <span>100%</span>
                        </div>
                    </div>
                </div>
                
                <div class="results-content">
                    <div class="file-comparison">
                        <h3><i class="fas fa-file-alt"></i> File Comparison</h3>
                        <div class="file-previews">
                            <div class="file-preview">
                                <div class="file-header">
                                    <h4>${data.file1_name}</h4>
                                    <span class="file-type">${data.file1_name.split('.').pop().toUpperCase()}</span>
                                </div>
                                <div class="file-content">
                                    <pre>${data.file1_preview}</pre>
                                </div>
                            </div>
                            
                            <div class="file-preview">
                                <div class="file-header">
                                    <h4>${data.file2_name}</h4>
                                    <span class="file-type">${data.file2_name.split('.').pop().toUpperCase()}</span>
                                </div>
                                <div class="file-content">
                                    <pre>${data.file2_preview}</pre>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="metrics-section">
                        <h3><i class="fas fa-tachometer-alt"></i> Detailed Metrics</h3>
                        <div class="metrics-grid" id="metrics-grid"></div>
                    </div>
                    
                    <div class="visualization-section">
                        <h3><i class="fas fa-th"></i> Similarity Heatmap</h3>
                        <div class="heatmap-container" id="heatmap"></div>
                        <div class="heatmap-legend">
                            <span>Low Similarity</span>
                            <div class="legend-gradient"></div>
                            <span>High Similarity</span>
                        </div>
                    </div>
                    
                    ${data.results.matches && data.results.matches.length > 0 ? `
                    <div class="matches-section">
                        <h3><i class="fas fa-code-compare"></i> Matched Sections</h3>
                        <div class="matches-container" id="matches-container"></div>
                    </div>
                    ` : ''}
                    
                    <div class="actions">
                        <button id="export-pdf" class="btn btn-primary">
                            <i class="fas fa-file-pdf"></i> Export PDF Report
                        </button>
                        <button id="new-analysis" class="btn btn-secondary">
                            <i class="fas fa-redo"></i> New Analysis
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        animateScore(scorePercent);
        renderMetrics(data.results.details);
        
        if (data.results.heatmap && typeof renderHeatmap === 'function') {
            renderHeatmap(data.results.heatmap);
        }
        
        if (data.results.matches && data.results.matches.length > 0) {
            renderMatches(data.results.matches, data.file1_preview, data.file2_preview);
        }
        
        document.getElementById('export-pdf').addEventListener('click', () => {
            exportAsPDF(data);
        });
        
        document.getElementById('new-analysis').addEventListener('click', () => {
            window.location.href = '/';
        });
        
        setTimeout(() => {
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }, 500);
        
        // Highlight code blocks if file type is code
        if (["python", "java", "cpp"].includes(data.type)) {
            setTimeout(() => {
                document.querySelectorAll('pre').forEach((block) => {
                    hljs.highlightElement(block);
                });
            }, 100);
        }
    }
    
    function animateScore(targetScore) {
        const scoreElement = document.getElementById('score-value');
        const progressFill = document.getElementById('progress-fill');
        let currentScore = 0;
        
        progressFill.style.backgroundColor = getScoreColor(targetScore / 100);
        
        const interval = setInterval(() => {
            currentScore += 1;
            scoreElement.textContent = `${currentScore}%`;
            progressFill.style.width = `${currentScore}%`;
            
            if (currentScore >= targetScore) {
                clearInterval(interval);
            }
        }, 20);
    }
    
    function getScoreColor(score) {
        if (score > 0.75) return 'var(--danger)';
        if (score > 0.5) return 'var(--warning)';
        if (score > 0.25) return 'var(--primary-light)';
        return 'var(--success)';
    }
    
    function renderMetrics(metrics) {
        const metricsGrid = document.getElementById('metrics-grid');
        metricsGrid.innerHTML = '';
        for (const [name, value] of Object.entries(metrics)) {
            const card = document.createElement('div');
            card.className = 'metric-card';
            card.innerHTML = `
                <div class="metric-icon" title="${getMetricTooltip(name)}">
                    ${getMetricIcon(name)}
                </div>
                <div class="metric-info">
                    <h4>${formatMetricName(name)}</h4>
                    <div class="metric-value">${(value * 100).toFixed(1)}%</div>
                </div>
            `;
            metricsGrid.appendChild(card);
        }
    }
    
    function getMetricIcon(metricName) {
        const icons = {
            'jaccard': 'fas fa-venus-double',
            'cosine': 'fas fa-vector-square',
            'levenshtein': 'fas fa-edit',
            'minhash': 'fas fa-fingerprint',
            'semantic': 'fas fa-brain',
            'ast_similarity': 'fas fa-project-diagram',
            'function_similarity': 'fas fa-code-branch'
        };
        return `<i class="${icons[metricName] || 'fas fa-ruler'}"></i>`;
    }
    
    function formatMetricName(name) {
        return name.split('_').map(word => 
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }
    
    function renderMatches(matches, content1, content2) {
        const container = document.getElementById('matches-container');
        
        matches.slice(0, 5).forEach(match => {
            const matchElement = document.createElement('div');
            matchElement.className = 'match-item';
            matchElement.innerHTML = `
                <div class="match-header">
                    <span class="similarity-badge">${Math.round(match.similarity * 100)}% match</span>
                    <span class="size-badge">${match.text1_end - match.text1_start} chars</span>
                </div>
                <div class="match-content">
                    <div class="match-side">
                        <span class="file-label">File 1</span>
                        <pre>${content1.substring(match.text1_start, match.text1_end)}</pre>
                    </div>
                    <div class="match-side">
                        <span class="file-label">File 2</span>
                        <pre>${content2.substring(match.text2_start, match.text2_end)}</pre>
                    </div>
                </div>
            `;
            container.appendChild(matchElement);
        });
    }
    
    function exportAsPDF(data) {
        const btn = document.getElementById('export-pdf');
        const originalContent = btn.innerHTML;
        
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
        btn.disabled = true;
        
        fetch('/export/pdf', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `plagiarism_report_${new Date().toISOString().slice(0,10)}.pdf`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(error => {
            showError('Failed to generate PDF: ' + error.message);
        })
        .finally(() => {
            btn.innerHTML = originalContent;
            btn.disabled = false;
        });
    }
    
    function showToast(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `<span>${message}</span>`;
        toastContainer.appendChild(toast);
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 500);
        }, 4000);
    }
    
    function getMetricTooltip(name) {
        const tooltips = {
            jaccard: 'Jaccard similarity measures word overlap.',
            cosine: 'Cosine similarity measures vector similarity.',
            levenshtein: 'Levenshtein distance measures edit distance.',
            minhash: 'MinHash estimates Jaccard similarity.',
            semantic: 'Semantic similarity uses language models.',
            ast_similarity: 'AST similarity compares code structure.',
            function_similarity: 'Function similarity compares function signatures.',
            logic_similarity: 'Logic similarity compares code logic.',
            variable_similarity: 'Variable usage similarity.',
            class_similarity: 'Class structure similarity (Java).',
            method_similarity: 'Method structure similarity (Java).',
            import_similarity: 'Import/include similarity.',
            include_similarity: 'Include similarity (C++).'
        };
        return tooltips[name] || name;
    }
    
    let loadingProgress = 0;
    let loadingInterval;

    function startLoadingProgress() {
        loadingProgress = 0;
        const fill = document.getElementById('loading-progress-fill');
        const text = document.getElementById('loading-progress-text');
        fill.style.width = '0%';
        text.textContent = 'Analyzing files... 0%';
        loadingInterval = setInterval(() => {
            if (loadingProgress < 70) {
                loadingProgress += 2; // Fast to 70
            } else if (loadingProgress < 99) {
                loadingProgress += 0.1; // Very slow from 70 to 99
            }
            if (loadingProgress > 99) loadingProgress = 99;
            fill.style.width = loadingProgress + '%';
            text.textContent = `Analyzing files... ${Math.floor(loadingProgress)}%`;
        }, 30);
    }

    function finishLoadingProgress() {
        clearInterval(loadingInterval);
        const fill = document.getElementById('loading-progress-fill');
        const text = document.getElementById('loading-progress-text');
        fill.style.width = '100%';
        text.textContent = 'Analyzing files... 100%';
    }
});