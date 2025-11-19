/**
 * 💬 Messenger Widget - Tích hợp Chatbot AI vào Django Blog
 * Features: Chat bubble, message history, soft colors, animations
 */

class MessengerWidget {
    constructor(options = {}) {
        this.isOpen = false;
        this.messages = [];
        this.isLoading = false;
        this.apiUrl = options.apiUrl || '/chatbot/api/chat/';
        this.healthCheckUrl = options.healthCheckUrl || '/chatbot/health/';
        this.botName = options.botName || 'Hinne 🥗';
        this.init();
    }

    init() {
        this.createWidget();
        this.attachEvents();
        this.addWelcomeMessage();
        this.checkHealth();
    }

    createWidget() {
        const html = `
        <div id="messenger-widget" class="messenger-widget" role="complementary" aria-label="Chat bot widget">
            <!-- Chat Bubble Button -->
            <div class="messenger-bubble" id="bubble" tabindex="0" role="button" aria-label="Open chat">
                <div class="bubble-icon">💬</div>
                <div class="bubble-pulse"></div>
            </div>

            <!-- Chat Window -->
            <div class="messenger-window hidden" id="window" role="dialog" aria-labelledby="window-title">
                <!-- Header -->
                <div class="window-header">
                    <div class="header-info">
                        <h3 id="window-title">${this.botName}</h3>
                        <span class="status-indicator" id="status">🟢 Online</span>
                    </div>
                    <button class="close-btn" id="close" aria-label="Close chat">✕</button>
                </div>

                <!-- Messages Container -->
                <div class="messages-container" id="messages" role="log" aria-live="polite">
                    <!-- Messages will be added here -->
                </div>

                <!-- Input Area -->
                <div class="input-area">
                    <input 
                        type="text" 
                        id="input" 
                        placeholder="Hỏi tôi về dinh dưỡng..."
                        aria-label="Message input"
                        autocomplete="off"
                    >
                    <button id="send" aria-label="Send message">
                        <span>➤</span>
                    </button>
                </div>
            </div>
        </div>
        `;

        document.body.insertAdjacentHTML('beforeend', html);
        this.addStyles();
    }

    addStyles() {
        const css = `
        <style>
            /* ===== MESSENGER WIDGET ===== */
            .messenger-widget {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 9999;
            }

            /* Bubble Button */
            .messenger-bubble {
                position: fixed;
                bottom: 20px;
                right: 20px;
                width: 70px;
                height: 70px;
                border-radius: 50%;
                background: linear-gradient(135deg, #FF7043 0%, #FFAB91 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                box-shadow: 0 4px 16px rgba(179, 157, 219, 0.4);
                z-index: 9998;
                transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
                user-select: none;
                border: none;
            }

            @media (max-width: 480px) {
                .messenger-bubble {
                    width: 60px;
                    height: 60px;
                    bottom: 15px;
                    right: 15px;
                }
            }

            @media (max-width: 320px) {
                .messenger-bubble {
                    width: 50px;
                    height: 50px;
                }
            }

            .messenger-bubble:hover {
                transform: scale(1.15);
                box-shadow: 0 6px 24px rgba(179, 157, 219, 0.6);
            }

            .messenger-bubble:active {
                transform: scale(0.95);
            }

            .bubble-icon {
                font-size: 32px;
                animation: bounce 2s ease-in-out infinite;
            }

            .bubble-pulse {
                position: absolute;
                width: 100%;
                height: 100%;
                border-radius: 50%;
                background: radial-gradient(circle, rgba(206, 147, 216, 0.4) 0%, transparent 70%);
                animation: pulse-ring 2s ease-out infinite;
            }

            @keyframes bounce {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-8px); }
            }

            @keyframes pulse-ring {
                0% {
                    transform: scale(0.8);
                    opacity: 1;
                }
                100% {
                    transform: scale(1.6);
                    opacity: 0;
                }
            }

            /* Chat Window */
            .messenger-window {
                position: fixed;
                bottom: 100px;
                right: 20px;
                width: min(400px, calc(100vw - 40px));
                height: min(600px, calc(100vh - 150px));
                background: white;
                border-radius: 16px;
                box-shadow: 0 8px 40px rgba(0, 0, 0, 0.2);
                z-index: 9999;
                display: flex;
                flex-direction: column;
                animation: slideInUp 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
            }

            /* Mobile Responsive */
            @media (max-width: 480px) {
                .messenger-window {
                    width: calc(100vw - 20px) !important;
                    height: calc(100vh - 100px) !important;
                    bottom: 80px;
                    right: 10px;
                    border-radius: 12px;
                }

                .messenger-bubble {
                    width: 60px;
                    height: 60px;
                    right: 10px;
                }

                .bubble-icon {
                    font-size: 28px;
                }
            }

            @media (max-width: 768px) {
                .messenger-window {
                    width: calc(100vw - 30px) !important;
                    height: calc(100vh - 120px) !important;
                }
            }

            .messenger-window.hidden {
                display: none;
                animation: slideOutDown 0.3s ease-in;
            }

            @keyframes slideInUp {
                from {
                    opacity: 0;
                    transform: translateY(40px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes slideOutDown {
                from {
                    opacity: 1;
                    transform: translateY(0);
                }
                to {
                    opacity: 0;
                    transform: translateY(40px);
                }
            }

            /* Window Header */
            .window-header {
                background: linear-gradient(135deg, #FF7043 0%, #FFAB91 100%);
                color: white;
                padding: 16px;
                border-radius: 16px 16px 0 0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                flex-shrink: 0;
            }

            .header-info h3 {
                margin: 0 0 4px 0;
                font-size: 16px;
                font-weight: 600;
                color: white;
            }

            .status-indicator {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.9);
                display: flex;
                align-items: center;
                gap: 4px;
            }

            .status-indicator.offline {
                color: #FFFFFF;
            }

            .close-btn {
                background: none;
                border: none;
                color: white;
                font-size: 24px;
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: transform 0.2s;
                border-radius: 4px;
            }

            .close-btn:hover {
                transform: scale(1.2);
                background: rgba(255, 255, 255, 0.2);
            }

            /* Messages Container */
            .messages-container {
                flex: 1;
                overflow-y: auto;
                padding: 10px;
                background: linear-gradient(135deg, rgba(248, 247, 249, 1) 0%, rgba(200, 230, 245, 0.1) 100%);
                display: flex;
                flex-direction: column;
                gap: 12px;
            }

            .messages-container::-webkit-scrollbar {
                width: 6px;
            }

            .messages-container::-webkit-scrollbar-track {
                background: transparent;
            }

            .messages-container::-webkit-scrollbar-thumb {
                background: rgba(206, 147, 216, 0.3);
                border-radius: 3px;
            }

            .messages-container::-webkit-scrollbar-thumb:hover {
                background: rgba(206, 147, 216, 0.5);
            }

            /* Message Styles */
            .message {
                display: flex;
                gap: 8px;
                animation: fadeInUp 0.3s ease-out;
            }

            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(10px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .message.user {
                justify-content: flex-end;
            }

            .message-content {
                max-width: 80%;
                padding: 10px 14px;
                font-size: 14px;
                line-height: 1.5;
                word-wrap: break-word;
                text-align: justify;
                white-space: pre-wrap;
                overflow-wrap: break-word;
            }

            .message.bot .message-content {
                background: linear-gradient(135deg, #c8e6f5 0%, rgba(127, 192, 217, 0.2) 100%);
                color: #333;
                border: 1px solid rgba(127, 192, 217, 0.3);
                border-radius: 0px 10px 10px 10px;
            }

            .message.user .message-content {
                background: linear-gradient(135deg, #FF7043 0%, #FFAB91 100%);
                color: white;
                text-align: right;
                border-radius: 10px 10px 0px 10px;
            }

            .message.system .message-content {
                background: rgba(206, 147, 216, 0.1);
                color: #666;
                font-size: 12px;
                text-align: center;
                max-width: 100%;
                padding: 8px;
                border-radius: 12px;
                border-radius: 6px;
                font-style: italic;
            }

            /* Loading Message (use a specific class to avoid global .loading spinner) */
            .message.loading-dots {
                justify-content: flex-start;
            }

            .message.loading-dots .message-content {
                display: flex;
                gap: 4px;
                align-items: center;
                background: transparent !important;
                border: none !important;
                padding: 0 !important;
                max-width: 100%;
            }

            .typing-dot {
                display: inline-block;
                width: 10px;
                height: 10px;
                background: linear-gradient(135deg, #A5D6A7, #81C784);
                border-radius: 50%;
                animation: typing-bounce 1.4s infinite ease-in-out;
                margin: 0 3px;
                box-shadow: 0 2px 8px rgba(165, 214, 167, 0.4);
            }

            .typing-dot:nth-child(2) {
                animation-delay: 0.2s;
            }

            .typing-dot:nth-child(3) {
                animation-delay: 0.4s;
            }

            @keyframes typing-bounce {
                0%, 60%, 100% {
                    transform: translateY(0) scale(1);
                    opacity: 0.6;
                }
                30% {
                    transform: translateY(-12px) scale(1.1);
                    opacity: 1;
                    box-shadow: 0 4px 12px rgba(165, 214, 167, 0.6);
                }
            }

            /* Typewriter caret for typing messages */
            .message-content.typing {
                position: relative;
                min-height: 18px;
                padding-right: 8px;
            }

            .message-content.typing::after {
                content: '';
                display: inline-block !important;
                width: 6px;
                height: 14px;
                margin-left: 6px;
                background: rgba(50,50,50,0.8);
                vertical-align: bottom;
                border-radius: 2px;
                animation: blink-caret 1s steps(1,end) infinite;
            }

            /* Remove cursor mark after typing completes */
            .message-content:not(.typing)::after {
                display: none !important;
            }

            /* Message metadata (time / source) */
            .message-meta {
                display: block;
                font-size: 11px;
                color: #999;
                margin-top: 6px;
                padding-top: 4px;
                border-top: 1px solid rgba(200,200,200,0.3);
            }

            .message-meta .time {
                font-size: 11px;
                color: #999;
                font-weight: normal;
                opacity: 0.8;
            }

            .message-meta .source {
                display: none;
            }

            @keyframes blink-caret {
                0% { opacity: 1; }
                50% { opacity: 0; }
                100% { opacity: 1; }
            }

            /* Input Area */
            .input-area {
                display: flex;
                gap: 8px;
                padding: 12px;
                background: white;
                border-top: 1px solid #e0e0e0;
                border-radius: 0 0 16px 16px;
                flex-shrink: 0;
            }

            #input {
                flex: 1;
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                padding: 10px 16px;
                font-size: 14px;
                outline: none;
                transition: all 0.2s;
                font-family: inherit;
            }

            #input:focus {
                border-color: #FF7043;
                box-shadow: 0 0 0 3px rgba(179, 157, 219, 0.1);
            }

            #send {
                background: linear-gradient(135deg, #FF7043 0%, #FFAB91 100%);
                color: white;
                border: none;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                cursor: pointer;
                font-size: 18px;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
            }

            #send:hover {
                transform: scale(1.1);
                box-shadow: 0 2px 8px rgba(179, 157, 219, 0.4);
            }

            #send:active {
                transform: scale(0.95);
            }

            #send:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            /* Mobile Responsive */
            @media (max-width: 600px) {
                .messenger-window {
                    width: calc(100vw - 20px);
                    height: calc(100vh - 100px);
                    bottom: 90px;
                    right: 10px;
                    border-radius: 12px;
                }

                .message-content {
                    max-width: 100%;
                }
            }

            /* Dark Mode Support */
            @media (prefers-color-scheme: dark) {
                .messenger-window {
                    background: #2a2a2a;
                }

                .messages-container {
                    background: #1e1e1e;
                }

                .message.bot .message-content {
                    background: rgba(127, 192, 217, 0.2);
                    color: #e0e0e0;
                }

                .message.system .message-content {
                    background: rgba(206, 147, 216, 0.15);
                    color: #b0b0b0;
                }

                #input {
                    background: #333;
                    color: #e0e0e0;
                    border-color: #444;
                }

                #input:focus {
                    border-color: #FF7043;
                    background: #3a3a3a;
                }

                .input-area {
                    background: #2a2a2a;
                    border-color: #444;
                }
            }
        </style>
        `;
        document.head.insertAdjacentHTML('beforeend', css);
    }

    attachEvents() {
        const bubble = document.getElementById('bubble');
        const window = document.getElementById('window');
        const closeBtn = document.getElementById('close');
        const sendBtn = document.getElementById('send');
        const input = document.getElementById('input');

        // Toggle window
        bubble.addEventListener('click', () => this.toggleWindow());
        closeBtn.addEventListener('click', () => this.toggleWindow());

        // Send message
        sendBtn.addEventListener('click', () => this.sendMessage());
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !this.isLoading) {
                this.sendMessage();
            }
        });

        // Auto-scroll
        const messagesContainer = document.getElementById('messages');
        const observer = new MutationObserver(() => {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        });
        observer.observe(messagesContainer, { childList: true });
    }

    toggleWindow() {
        const window = document.getElementById('window');
        this.isOpen = !this.isOpen;

        if (this.isOpen) {
            window.classList.remove('hidden');
            setTimeout(() => {
                document.getElementById('input').focus();
            }, 200);
        } else {
            window.classList.add('hidden');
        }
    }

    addWelcomeMessage() {
        setTimeout(() => {
            this.addMessage(
                `👋 Chào bạn! Tôi là ${this.botName}. Hãy hỏi tôi về dinh dưỡng, thể hình, cũng như bài tập nhé!`,
                'bot'
            );
        }, 500);
    }

    sendMessage() {
        const input = document.getElementById('input');
        const query = input.value.trim();

        if (!query || this.isLoading) return;

        // Hiển thị tin nhắn user
        this.addMessage(query, 'user');
        input.value = '';

        // Gửi đến API
        this.callAPI(query);
    }

    addMessage(text, sender = 'bot') {
        const container = document.getElementById('messages');
        const div = document.createElement('div');
        div.className = `message ${sender}`;

        const content = document.createElement('div');
        content.className = 'message-content';

        if (sender === 'loading') {
            content.innerHTML = `
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            `;
            // use loading-dots to avoid global .loading spinner in styles.css
            div.className = 'message loading-dots';
        } else {
            content.textContent = text;
        }

        div.appendChild(content);
        container.appendChild(div);

        return div;
    }

    // Typewriter effect for bot responses (animates characters one-by-one)
    // meta: optional object { timestamp: 'ISO string', source: '...' }
    typeText(text, speed = 18, meta = {}) {
        const container = document.getElementById('messages');
        const div = document.createElement('div');
        div.className = 'message bot';

        const content = document.createElement('div');
        content.className = 'message-content typing';
        content.textContent = '';

        div.appendChild(content);
        container.appendChild(div);

        let idx = 0;
        const step = () => {
            if (idx < text.length) {
                content.textContent += text.charAt(idx);
                idx += 1;
                // small random jitter to feel more human
                const jitter = speed + Math.floor(Math.random() * 10) - 5;
                content._timer = setTimeout(step, Math.max(8, jitter));
            } else {
                // finished
                if (content._timer) {
                    clearTimeout(content._timer);
                }
                // Remove typing indicator (cursor mark)
                content.classList.remove('typing');
                // append metadata if provided
                if (meta && (meta.timestamp || meta.source)) {
                    const metaEl = document.createElement('div');
                    metaEl.className = 'message-meta';
                    // Only show timestamp, hide source (API endpoint)
                    const timePart = meta.timestamp ? `<span class="time">${new Date(meta.timestamp).toLocaleTimeString()}</span>` : '';
                    metaEl.innerHTML = timePart;
                    content.appendChild(metaEl);
                }
            }
        };

        // Start typing after a tiny pause to make transition from "typing dots" natural
        setTimeout(step, 120);

        return div;
    }

    callAPI(query) {
        const container = document.getElementById('messages');
        const sendBtn = document.getElementById('send');

        // Loading state
        this.isLoading = true;
        sendBtn.disabled = true;
        const loadingDiv = this.addMessage('', 'loading');

        fetch(this.apiUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query }),
            timeout: 35000,
        })
            .then((res) => {
                if (!res.ok) {
                    throw new Error(`HTTP ${res.status}`);
                }
                return res.json();
            })
            .then((data) => {
                container.removeChild(loadingDiv);

                if (data.success) {
                    // Show bot response with typing animation and pass metadata
                    const meta = { timestamp: data.timestamp, source: data.source };
                    this.typeText(data.response, 18, meta);
                } else {
                    this.addMessage(
                        `❌ ${data.error || 'Có lỗi xảy ra'}`,
                        'bot'
                    );
                    this.updateStatus('offline');
                }
            })
            .catch((err) => {
                container.removeChild(loadingDiv);
                this.addMessage(
                    `❌ Lỗi kết nối: ${err.message}. Hãy thử lại!`,
                    'bot'
                );
                this.updateStatus('offline');
            })
            .finally(() => {
                this.isLoading = false;
                sendBtn.disabled = false;
                document.getElementById('input').focus();
            });
    }

    checkHealth() {
        fetch(this.healthCheckUrl)
            .then((res) => res.json())
            .then((data) => {
                if (data.success) {
                    this.updateStatus('online');
                } else {
                    this.updateStatus('offline');
                }
            })
            .catch(() => {
                this.updateStatus('offline');
            });

        // Check every 30 seconds
        setInterval(() => {
            fetch(this.healthCheckUrl)
                .then((res) => res.json())
                .then((data) => {
                    if (data.success) {
                        this.updateStatus('online');
                    }
                })
                .catch(() => {
                    this.updateStatus('offline');
                });
        }, 30000);
    }

    updateStatus(status) {
        const statusIndicator = document.getElementById('status');
        if (statusIndicator) {
            if (status === 'online') {
                statusIndicator.textContent = '🟢 Online';
                statusIndicator.classList.remove('offline');
            } else {
                statusIndicator.textContent = '🔴 Offline';
                statusIndicator.classList.add('offline');
            }
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new MessengerWidget({
        apiUrl: '/chatbot/api/chat/',
        healthCheckUrl: '/chatbot/health/',
        botName: 'Hinne 🥗',
    });
});
