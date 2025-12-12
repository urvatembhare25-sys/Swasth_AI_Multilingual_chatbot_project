document.addEventListener('DOMContentLoaded', () => {
    // Theme Toggle
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;
    const icon = themeToggle.querySelector('i');

    // Check local storage
    if (localStorage.getItem('theme') === 'light') {
        html.setAttribute('data-theme', 'light');
        icon.classList.replace('fa-moon', 'fa-sun');
    }

    themeToggle.addEventListener('click', () => {
        if (html.getAttribute('data-theme') === 'dark') {
            html.setAttribute('data-theme', 'light');
            icon.classList.replace('fa-moon', 'fa-sun');
            localStorage.setItem('theme', 'light');
        } else {
            html.setAttribute('data-theme', 'dark'); // Remove attribute to fallback to root (dark) or set explicitly
            icon.classList.replace('fa-sun', 'fa-moon');
            localStorage.setItem('theme', 'dark');
        }
    });

    // Chat Logic
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('chat-messages');
    const welcomeScreen = document.getElementById('welcome-screen');
    const langSelect = document.getElementById('language-select');

    function appendMessage(text, sender) {
        welcomeScreen.style.display = 'none';
        messagesContainer.style.display = 'flex';

        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', sender);
        msgDiv.textContent = text;
        messagesContainer.appendChild(msgDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async function sendMessage(text) {
        if (!text.trim()) return;

        appendMessage(text, 'user');
        chatInput.value = '';
        chatInput.style.height = '56px'; // Reset height

        const lang = langSelect.value;
        const loadingDiv = document.createElement('div');
        loadingDiv.classList.add('message', 'bot');
        loadingDiv.textContent = '...';
        messagesContainer.appendChild(loadingDiv);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text, language: lang })
            });

            const data = await response.json();
            messagesContainer.removeChild(loadingDiv);

            if (data.response) {
                appendMessage(data.response, 'bot');
            } else {
                appendMessage("Sorry, I encountered an error.", 'bot');
            }
        } catch (error) {
            messagesContainer.removeChild(loadingDiv);
            appendMessage("Network error. Please try again.", 'bot');
        }
    }

    sendBtn.addEventListener('click', () => sendMessage(chatInput.value));

    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage(chatInput.value);
        }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
        if (this.value === '') this.style.height = '56px';
    });
});

function startNewChat() {
    document.getElementById('chat-messages').innerHTML = '';
    document.getElementById('chat-messages').style.display = 'none';
    document.getElementById('welcome-screen').style.display = 'block';
}

function sendQuickMessage(text) {
    const input = document.getElementById('chat-input');
    input.value = text;
    document.getElementById('send-btn').click();
}

function loadHistoryItem(element) {
    const msg = element.getAttribute('data-message');
    const res = element.getAttribute('data-response');

    // Switch to chat view
    document.getElementById('welcome-screen').style.display = 'none';
    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.style.display = 'flex';
    messagesContainer.innerHTML = ''; // Clear current

    // Re-render the exchange
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', 'user');
    msgDiv.textContent = msg;
    messagesContainer.appendChild(msgDiv);

    const resDiv = document.createElement('div');
    resDiv.classList.add('message', 'bot');
    resDiv.textContent = res;
    messagesContainer.appendChild(resDiv);

    // Mobile: close sidebar on selection
    if (window.innerWidth <= 768) {
        toggleSidebar();
    }
}

function toggleSidebar() {
    const sidebar = document.getElementById('chat-sidebar');
    const overlay = document.getElementById('chat-overlay');
    if (sidebar && overlay) {
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    }
}

async function deleteChat(event, chatId) {
    event.stopPropagation(); // Prevent opening the chat
    if (!confirm('Are you sure you want to delete this chat?')) return;

    try {
        const response = await fetch(`/delete_chat/${chatId}`, {
            method: 'DELETE'
        });

        const contentType = response.headers.get("content-type");
        if (!contentType || !contentType.includes("application/json")) {
            const text = await response.text();
            console.error('Non-JSON response:', text);
            throw new Error('Server returned non-JSON response');
        }

        const data = await response.json();

        if (data.success) {
            // Remove element from DOM
            const btn = event.currentTarget;
            const item = btn.closest('.history-item');
            if (item) item.remove();
        } else {
            console.error('Delete failed:', data);
            alert('Failed to delete chat: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error in deleteChat:', error);
        alert('Error deleting chat. Check console for details.');
    }
}

// Modal Functions
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'block';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
}

window.onclick = function (event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = "none";
    }
}
