/**
 * WebSocket Client for Real-Time Dealership Contact Automation
 *
 * Handles:
 * - WebSocket connection management
 * - Event handling and callbacks
 * - Automatic reconnection
 * - Screenshot receiving and display
 */

class DealershipWebSocketClient {
    constructor(url = 'ws://localhost:8001/ws/contact') {
        this.url = url;
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 2000;

        // Event handlers
        this.handlers = {
            connected: [],
            disconnected: [],
            contact_started: [],
            navigation_started: [],
            contact_page_found: [],
            captcha_detected: [],
            form_not_found: [],
            form_detected: [],
            filling_form: [],
            form_filled: [],
            submitting: [],
            contact_success: [],
            contact_failed: [],
            contact_error: [],
            contact_complete: [],
            screenshot: []
        };
    }

    /**
     * Connect to WebSocket server
     */
    connect() {
        return new Promise((resolve, reject) => {
            console.log(`[WebSocket] Connecting to ${this.url}...`);

            try {
                this.ws = new WebSocket(this.url);

                this.ws.onopen = () => {
                    console.log('[WebSocket] Connected successfully');
                    this.isConnected = true;
                    this.reconnectAttempts = 0;
                    this.trigger('connected');
                    resolve();
                };

                this.ws.onmessage = (event) => {
                    try {
                        const message = JSON.parse(event.data);
                        this.handleMessage(message);
                    } catch (error) {
                        console.error('[WebSocket] Error parsing message:', error);
                    }
                };

                this.ws.onerror = (error) => {
                    console.error('[WebSocket] Error:', error);
                    reject(error);
                };

                this.ws.onclose = () => {
                    console.log('[WebSocket] Connection closed');
                    this.isConnected = false;
                    this.trigger('disconnected');
                    // Let app-level reconnection logic handle reconnection
                    // this.attemptReconnect(); // DISABLED: app handles reconnection
                };

            } catch (error) {
                console.error('[WebSocket] Connection failed:', error);
                reject(error);
            }
        });
    }

    /**
     * Disconnect from WebSocket server
     */
    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.isConnected = false;
        }
    }

    /**
     * Attempt to reconnect
     */
    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[WebSocket] Max reconnect attempts reached');
            return;
        }

        this.reconnectAttempts++;
        console.log(`[WebSocket] Reconnecting in ${this.reconnectDelay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);

        setTimeout(() => {
            this.connect().catch(error => {
                console.error('[WebSocket] Reconnect failed:', error);
            });
        }, this.reconnectDelay);
    }

    /**
     * Handle incoming message
     */
    handleMessage(message) {
        console.log('[WebSocket] Received:', message.type, message.data);

        const eventType = message.type;

        if (this.handlers[eventType]) {
            this.handlers[eventType].forEach(handler => {
                try {
                    handler(message.data, message.timestamp);
                } catch (error) {
                    console.error(`[WebSocket] Error in ${eventType} handler:`, error);
                }
            });
        }
    }

    /**
     * Register event handler
     */
    on(event, handler) {
        if (this.handlers[event]) {
            this.handlers[event].push(handler);
        } else {
            console.warn(`[WebSocket] Unknown event type: ${event}`);
        }
    }

    /**
     * Remove event handler
     */
    off(event, handler) {
        if (this.handlers[event]) {
            const index = this.handlers[event].indexOf(handler);
            if (index > -1) {
                this.handlers[event].splice(index, 1);
            }
        }
    }

    /**
     * Trigger event handlers
     */
    trigger(event, data = null) {
        if (this.handlers[event]) {
            this.handlers[event].forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`[WebSocket] Error triggering ${event}:`, error);
                }
            });
        }
    }

    /**
     * Send contact request to backend
     */
    async contactDealer(dealership, customerInfo) {
        if (!this.isConnected) {
            throw new Error('WebSocket not connected');
        }

        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.isConnected = false;
            throw new Error('WebSocket connection not in OPEN state');
        }

        const message = {
            type: 'contact_dealer',
            dealership: {
                dealer_name: dealership.dealer_name,
                website: dealership.website,
                city: dealership.city,
                state: dealership.state
            },
            customer_info: {
                firstName: customerInfo.firstName,
                lastName: customerInfo.lastName,
                email: customerInfo.email,
                phone: customerInfo.phone,
                zipcode: customerInfo.zipcode,
                message: customerInfo.message
            }
        };

        console.log('[WebSocket] Sending contact request:', message);

        try {
            this.ws.send(JSON.stringify(message));
        } catch (error) {
            console.error('[WebSocket] Send failed:', error);
            this.isConnected = false;
            throw new Error(`Failed to send message: ${error.message}`);
        }
    }

    /**
     * Send ping to keep connection alive
     */
    ping() {
        if (this.isConnected) {
            this.ws.send(JSON.stringify({ type: 'ping' }));
        }
    }

    /**
     * Start ping interval
     */
    startPingInterval(interval = 30000) {
        // Clear existing interval first to prevent accumulation
        this.stopPingInterval();

        this.pingInterval = setInterval(() => {
            this.ping();
        }, interval);
    }

    /**
     * Stop ping interval
     */
    stopPingInterval() {
        if (this.pingInterval) {
            clearInterval(this.pingInterval);
            this.pingInterval = null;
        }
    }
}

// Export for use in main app
window.DealershipWebSocketClient = DealershipWebSocketClient;
