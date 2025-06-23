// Global variables
let baseUrl = 'http://localhost:5000/api';

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    checkApiStatus();
    setupNavigation();
    loadSavedToken();
});

// Check API status
async function checkApiStatus() {
    try {
        const response = await fetch(`${baseUrl}/health`);
        const data = await response.json();
        
        const statusElement = document.getElementById('api-status');
        if (response.ok) {
            statusElement.className = 'badge bg-success';
            statusElement.textContent = '✅ API Online';
        } else {
            statusElement.className = 'badge bg-danger';
            statusElement.textContent = '❌ API Error';
        }
    } catch (error) {
        const statusElement = document.getElementById('api-status');
        statusElement.className = 'badge bg-danger';
        statusElement.textContent = '❌ API Offline';
    }
}

// Setup navigation
function setupNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Remove active class from all links
            navLinks.forEach(l => l.classList.remove('active'));
            
            // Add active class to clicked link
            this.classList.add('active');
            
            // Scroll to section
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
}

// Load saved token
function loadSavedToken() {
    const savedToken = localStorage.getItem('authToken');
    if (savedToken) {
        document.getElementById('authToken').value = savedToken;
    }
}

// Save token to localStorage
function saveToken(token) {
    localStorage.setItem('authToken', token);
    document.getElementById('authToken').value = token;
}

// Change base URL
function changeBaseUrl() {
    const newUrl = prompt('Ingresa la nueva URL base:', baseUrl);
    if (newUrl) {
        baseUrl = newUrl.replace(/\/$/, ''); // Remove trailing slash
        document.getElementById('baseUrl').textContent = baseUrl;
        checkApiStatus();
    }
}

// Make API request
async function makeRequest(method, endpoint, bodyElementId = null) {
    const url = `${baseUrl}${endpoint}`;
    const responseElementId = `response-${endpoint.replace(/[\/]/g, '-').replace(/^-/, '')}`;
    
    // Get auth token
    const token = document.getElementById('authToken').value;
    
    // Prepare headers
    const headers = {
        'Content-Type': 'application/json'
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    // Prepare request options
    const options = {
        method: method,
        headers: headers
    };
    
    // Add body for POST/PUT requests
    if (bodyElementId && (method === 'POST' || method === 'PUT')) {
        const bodyElement = document.getElementById(bodyElementId);
        if (bodyElement) {
            try {
                const bodyText = bodyElement.value;
                JSON.parse(bodyText); // Validate JSON
                options.body = bodyText;
            } catch (error) {
                showResponse(responseElementId, {
                    error: 'JSON inválido en el cuerpo de la petición',
                    details: error.message
                }, false);
                return;
            }
        }
    }
    
    // Show loading
    showResponse(responseElementId, { message: '⏳ Enviando petición...' }, true);
    
    try {
        const response = await fetch(url, options);
        const data = await response.json();
        
        // Show response
        showResponse(responseElementId, data, response.ok);
        
        // Auto-save token if login successful
        if (endpoint === '/auth/login' && response.ok && data.access_token) {
            saveToken(data.access_token);
            showNotification('Token guardado automáticamente', 'success');
        }
        
    } catch (error) {
        showResponse(responseElementId, {
            error: 'Error de conexión',
            details: error.message
        }, false);
    }
}

// Show response in UI
function showResponse(elementId, data, isSuccess) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.style.display = 'block';
    element.innerHTML = `
        <div class="d-flex justify-content-between align-items-center mb-2">
            <strong>${isSuccess ? '✅ Respuesta' : '❌ Error'}</strong>
            <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard('${elementId}')">
                📋 Copiar
            </button>
        </div>
        <pre><code class="language-json">${JSON.stringify(data, null, 2)}</code></pre>
    `;
    
    // Highlight syntax
    if (window.Prism) {
        Prism.highlightAllUnder(element);
    }
}

// Copy response to clipboard
function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    const codeElement = element.querySelector('code');
    if (codeElement) {
        navigator.clipboard.writeText(codeElement.textContent).then(() => {
            showNotification('Respuesta copiada al portapapeles', 'success');
        });
    }
}

// Show notification
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Auto-set token from login response
function autoSetToken(responseType) {
    const responseElement = document.getElementById(`response-${responseType}`);
    if (responseElement) {
        const codeElement = responseElement.querySelector('code');
        if (codeElement) {
            try {
                const data = JSON.parse(codeElement.textContent);
                if (data.access_token) {
                    saveToken(data.access_token);
                    showNotification('Token guardado automáticamente', 'success');
                } else {
                    showNotification('No se encontró token en la respuesta', 'warning');
                }
            } catch (error) {
                showNotification('Error al extraer token', 'danger');
            }
        }
    }
}

// Get products with filters
function getProducts() {
    const search = document.getElementById('product-search').value;
    const minPrice = document.getElementById('product-min-price').value;
    const maxPrice = document.getElementById('product-max-price').value;
    
    let endpoint = '/products';
    const params = new URLSearchParams();
    
    if (search) params.append('q', search);
    if (minPrice) params.append('min_price', minPrice);
    if (maxPrice) params.append('max_price', maxPrice);
    
    if (params.toString()) {
        endpoint += '?' + params.toString();
    }
    
    makeRequest('GET', endpoint);
}

// Utility functions for common operations
function quickLogin() {
    document.getElementById('login-body').value = JSON.stringify({
        email: 'admin@test.com',
        password: 'admin123'
    }, null, 2);
    makeRequest('POST', '/auth/login', 'login-body');
}

function quickUserLogin() {
    document.getElementById('login-body').value = JSON.stringify({
        email: 'user@test.com',
        password: 'user123'
    }, null, 2);
    makeRequest('POST', '/auth/login', 'login-body');
}

// Add quick login buttons
document.addEventListener('DOMContentLoaded', function() {
    // Add quick login buttons to login section
    const loginCard = document.querySelector('#auth .endpoint-card:nth-child(2) .card-body');
    if (loginCard) {
        const quickButtons = document.createElement('div');
        quickButtons.className = 'mt-2';
        quickButtons.innerHTML = `
            <button class="btn btn-sm btn-outline-primary me-2" onclick="quickLogin()">
                👑 Login Admin
            </button>
            <button class="btn btn-sm btn-outline-secondary" onclick="quickUserLogin()">
                👤 Login Usuario
            </button>
        `;
        loginCard.appendChild(quickButtons);
    }
});

// Add example data helpers
function fillExampleProduct() {
    const productBody = document.getElementById('add-cart-body');
    if (productBody) {
        // This would be filled with actual product ID from the products response
        showNotification('Primero obtén un producto para usar su ID', 'info');
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl + Enter to send request in focused textarea
    if (e.ctrlKey && e.key === 'Enter') {
        const activeElement = document.activeElement;
        if (activeElement.tagName === 'TEXTAREA') {
            const card = activeElement.closest('.card');
            const button = card.querySelector('button[onclick*="makeRequest"]');
            if (button) {
                button.click();
            }
        }
    }
});

// Add help tooltip
document.addEventListener('DOMContentLoaded', function() {
    const helpTooltip = document.createElement('div');
    helpTooltip.className = 'position-fixed bg-dark text-white p-2 rounded';
    helpTooltip.style.cssText = 'bottom: 20px; left: 20px; font-size: 0.8em; z-index: 9999;';
    helpTooltip.innerHTML = '💡 Tip: Usa Ctrl+Enter en cualquier textarea para enviar la petición';
    document.body.appendChild(helpTooltip);
    
    // Hide after 5 seconds
    setTimeout(() => {
        helpTooltip.style.opacity = '0.5';
    }, 5000);
});
