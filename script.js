const shortenForm = document.getElementById('shortenForm');
const longUrlInput = document.getElementById('longUrl');
const resultDiv = document.getElementById('result');
const shortUrlInput = document.getElementById('shortUrlInput');
const copyBtn = document.getElementById('copyBtn');
const errorMessage = document.getElementById('errorMessage');
const loadingDiv = document.getElementById('loading');

const API_URL = 'http://127.0.0.1:8000';

shortenForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const longUrl = longUrlInput.value.trim();
    
    if (!longUrl) {
        showError('Please enter a URL');
        return;
    }

    try {
        showLoading(true);
        hideError();
        hideResult();

        const response = await fetch(`${API_URL}/shorten`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ long_url: longUrl }),
        });

        if (!response.ok) {
            throw new Error('Failed to shorten URL');
        }

        const data = await response.json();
        shortUrlInput.value = data.short_url;
        showResult();
        longUrlInput.value = '';
    } catch (error) {
        showError('Error: ' + (error.message || 'Something went wrong'));
    } finally {
        showLoading(false);
    }
});

copyBtn.addEventListener('click', () => {
    shortUrlInput.select();
    document.execCommand('copy');
    
    const originalText = copyBtn.textContent;
    copyBtn.textContent = 'Copied!';
    
    setTimeout(() => {
        copyBtn.textContent = originalText;
    }, 2000);
});

// Also allow copying by selecting the input and pressing Ctrl+C
shortUrlInput.addEventListener('click', () => {
    shortUrlInput.select();
});

function showResult() {
    resultDiv.classList.remove('hidden');
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideResult() {
    resultDiv.classList.add('hidden');
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
}

function showLoading(show) {
    if (show) {
        loadingDiv.classList.remove('hidden');
    } else {
        loadingDiv.classList.add('hidden');
    }
}
