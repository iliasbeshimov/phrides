/**
 * WebSocket Integration Methods
 *
 * Add these methods to your Vue app's methods section
 */

const websocketMethods = {
    // ========== WebSocket Connection Management ==========

    async initializeWebSocket() {
        console.log('[App] Initializing WebSocket connection...');
        this.websocketStatus = 'connecting';

        // Track reconnection attempts at app level
        if (!this.wsReconnectAttempts) this.wsReconnectAttempts = 0;

        if (this.wsReconnectAttempts >= 3) {
            console.error('[App] Max WebSocket reconnect attempts reached');
            this.websocketStatus = 'failed';
            alert('Cannot connect to automation server.\n\nPlease ensure the backend is running:\ncd backend && python websocket_server.py');
            return;
        }

        this.wsReconnectAttempts++;

        // Stop existing client before creating new one
        if (this.websocketClient) {
            try {
                this.websocketClient.stopPingInterval();
                this.websocketClient.disconnect();
            } catch (e) {
                console.error('[App] Error cleaning up old WebSocket client:', e);
            }
        }

        try {
            this.websocketClient = new DealershipWebSocketClient(this.websocketUrl);

            // Register event handlers
            this.setupWebSocketHandlers();

            // Connect
            await this.websocketClient.connect();

            this.websocketStatus = 'connected';
            this.wsReconnectAttempts = 0; // Reset on success
            console.log('[App] WebSocket connected successfully');

            // Start ping interval to keep connection alive
            this.websocketClient.startPingInterval(30000);

        } catch (error) {
            console.error('[App] WebSocket connection failed:', error);
            this.websocketStatus = 'disconnected';

            // Retry connection after delay (if not exceeded max attempts)
            if (this.wsReconnectAttempts < 3) {
                console.log(`[App] Will retry connection in 5 seconds (attempt ${this.wsReconnectAttempts}/3)...`);
                setTimeout(() => {
                    this.initializeWebSocket();
                }, 5000);
            }
        }
    },

    setupWebSocketHandlers() {
        const client = this.websocketClient;

        // Connection events
        client.on('connected', () => {
            this.websocketStatus = 'connected';
            console.log('[App] WebSocket handlers registered');
        });

        client.on('disconnected', () => {
            this.websocketStatus = 'disconnected';
            this.contactInProgress = false;  // Reset flag on disconnect
        });

        // Contact process events - all wrapped in error boundaries
        client.on('contact_started', (data) => {
            try {
                console.log('[Contact] Started:', data?.dealer_name || 'Unknown');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid contact_started data:', data);
                    return;
                }
                this.updateDealerStatus(data.dealer_name, 'contacting', 'Contacting dealer...');
            } catch (error) {
                console.error('[Contact] Error in contact_started handler:', error);
            }
        });

        client.on('navigation_started', (data) => {
            try {
                console.log('[Contact] Navigating to:', data?.url || 'Unknown URL');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid navigation_started data:', data);
                    return;
                }
                this.updateDealerStatus(data.dealer_name, 'contacting', 'Navigating to website...');
            } catch (error) {
                console.error('[Contact] Error in navigation_started handler:', error);
            }
        });

        client.on('contact_page_found', (data) => {
            try {
                console.log('[Contact] Contact page found:', data?.contact_url || 'Unknown');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid contact_page_found data:', data);
                    return;
                }
                const fieldCount = data.form_field_count || 0;
                this.updateDealerStatus(data.dealer_name, 'contacting', `Found contact page (${fieldCount} fields)`);
            } catch (error) {
                console.error('[Contact] Error in contact_page_found handler:', error);
            }
        });

        client.on('captcha_detected', (data) => {
            try {
                console.log('[Contact] CAPTCHA detected:', data?.captcha_type || 'Unknown type');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid captcha_detected data:', data);
                    return;
                }

                // Update dealer with CAPTCHA info
                this.updateDealerWithResult(data.dealer_name, {
                    success: false,
                    reason: 'captcha_detected',
                    details: `${data.captcha_type || 'CAPTCHA'} detected - manual intervention required`,
                    contact_url: data.contact_url || null,
                    captcha_type: data.captcha_type || 'Unknown',
                    screenshots: data.screenshot_url ? [data.screenshot_url] : []
                });

                // Show notification
                this.showNotification('warning', `CAPTCHA Detected: ${data.dealer_name}`, `${data.captcha_type || 'CAPTCHA'} requires manual filling`);
            } catch (error) {
                console.error('[Contact] Error in captcha_detected handler:', error);
            }
        });

        client.on('form_not_found', (data) => {
            try {
                console.log('[Contact] Form not found:', data?.dealer_name || 'Unknown');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid form_not_found data:', data);
                    return;
                }

                this.updateDealerWithResult(data.dealer_name, {
                    success: false,
                    reason: 'form_not_found',
                    details: data.reason || 'Could not locate contact form',
                    contact_url: null,
                    screenshots: []
                });

                this.showNotification('error', `Form Not Found: ${data.dealer_name}`, 'Could not locate contact form on website');
            } catch (error) {
                console.error('[Contact] Error in form_not_found handler:', error);
            }
        });

        client.on('form_detected', (data) => {
            try {
                console.log('[Contact] Form detected:', data?.field_count || 0, 'fields');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid form_detected data:', data);
                    return;
                }
                const fieldCount = data.field_count || 0;
                const confidence = (data.confidence || 0) * 100;
                this.updateDealerStatus(data.dealer_name, 'contacting', `Form detected (${fieldCount} fields, confidence: ${confidence.toFixed(0)}%)`);
            } catch (error) {
                console.error('[Contact] Error in form_detected handler:', error);
            }
        });

        client.on('filling_form', (data) => {
            try {
                console.log('[Contact] Filling form...');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid filling_form data:', data);
                    return;
                }
                this.updateDealerStatus(data.dealer_name, 'contacting', 'Filling form fields...');
            } catch (error) {
                console.error('[Contact] Error in filling_form handler:', error);
            }
        });

        client.on('form_filled', (data) => {
            try {
                console.log('[Contact] Form filled, screenshot available');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid form_filled data:', data);
                    return;
                }
                this.updateDealerStatus(data.dealer_name, 'contacting', 'Form filled, preparing submission...');
            } catch (error) {
                console.error('[Contact] Error in form_filled handler:', error);
            }
        });

        client.on('submitting', (data) => {
            try {
                console.log('[Contact] Submitting form...');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid submitting data:', data);
                    return;
                }
                this.updateDealerStatus(data.dealer_name, 'contacting', 'Submitting form...');
            } catch (error) {
                console.error('[Contact] Error in submitting handler:', error);
            }
        });

        client.on('contact_success', (data) => {
            try {
                console.log('[Contact] SUCCESS:', data?.dealer_name || 'Unknown');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid contact_success data:', data);
                    return;
                }

                this.updateDealerWithResult(data.dealer_name, {
                    success: true,
                    reason: 'success',
                    details: `Successfully submitted via ${data.submission_method || 'unknown method'} (verified: ${data.verification || 'unknown'})`,
                    contact_url: data.contact_url || null,
                    screenshots: data.screenshot_url ? [data.screenshot_url] : []
                });

                this.showNotification('success', `Success: ${data.dealer_name}`, 'Contact form submitted successfully!');
            } catch (error) {
                console.error('[Contact] Error in contact_success handler:', error);
            }
        });

        client.on('contact_failed', (data) => {
            try {
                console.log('[Contact] FAILED:', data?.dealer_name || 'Unknown', data?.blocker || 'Unknown reason');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid contact_failed data:', data);
                    return;
                }

                this.updateDealerWithResult(data.dealer_name, {
                    success: false,
                    reason: data.blocker || 'submission_failed',
                    details: data.error || 'Form submission failed',
                    contact_url: data.contact_url || null,
                    screenshots: data.screenshot_url ? [data.screenshot_url] : []
                });

                this.showNotification('error', `Failed: ${data.dealer_name}`, data.error || 'Submission failed');
            } catch (error) {
                console.error('[Contact] Error in contact_failed handler:', error);
            }
        });

        client.on('contact_error', (data) => {
            try {
                console.error('[Contact] ERROR:', data?.error || 'Unknown error');
                if (!data || !data.dealer_name) {
                    console.error('[Contact] Invalid contact_error data:', data);
                    return;
                }

                this.updateDealerWithResult(data.dealer_name, {
                    success: false,
                    reason: 'error',
                    details: data.error || 'Unknown error occurred',
                    contact_url: null,
                    screenshots: []
                });

                this.showNotification('error', `Error: ${data.dealer_name}`, data.error || 'Unknown error');
            } catch (error) {
                console.error('[Contact] Error in contact_error handler:', error);
            }
        });

        client.on('contact_complete', (data) => {
            try {
                console.log('[Contact] Complete:', data?.result || 'No result data');

                // Mark current contact as complete
                this.contactInProgress = false;

                // Clear any existing timer first (prevent stacking)
                if (this.contactNextTimer) {
                    clearTimeout(this.contactNextTimer);
                    this.contactNextTimer = null;
                }

                // Move to next dealer if in batch mode
                if (this.contactState === 'running') {
                    // Small delay before next dealer
                    this.contactNextTimer = setTimeout(() => {
                        this.contactNextDealer();
                        this.contactNextTimer = null;
                    }, 2000);
                }
            } catch (error) {
                console.error('[Contact] Error in contact_complete handler:', error);
            }
        });
    },

    // ========== Dealer Contact Methods (WebSocket-based) ==========

    async contactSingleDealer(dealer) {
        if (!this.websocketClient || !this.websocketClient.isConnected) {
            alert('Not connected to automation server. Please check if the backend is running.');
            return;
        }

        // Prevent concurrent contact attempts for same dealer
        if (dealer.contactStatus === 'contacting') {
            console.warn(`[App] Dealer ${dealer.dealer_name} already being contacted, ignoring duplicate request`);
            return;
        }

        console.log('[App] Contacting single dealer:', dealer.dealer_name);

        this.currentDealer = dealer;
        dealer.contactStatus = 'contacting';
        dealer.contactStartTime = Date.now();

        // Set timeout to auto-reset status if stuck (2 minutes max)
        const timeoutId = setTimeout(() => {
            if (dealer.contactStatus === 'contacting') {
                console.warn(`[App] Dealer ${dealer.dealer_name} stuck in 'contacting' for 2 minutes, auto-resetting to 'failed'`);
                dealer.contactStatus = 'failed';
                dealer.statusMessage = 'Contact timeout - no response from server';
                this.showNotification('error', `Timeout: ${dealer.dealer_name}`, 'No response from server after 2 minutes');
            }

            // CRITICAL: Always reset flag, even if status already changed
            this.contactInProgress = false;

            // Move to next dealer if in batch mode
            if (this.contactState === 'running') {
                console.log('[Timeout] Moving to next dealer after timeout');
                setTimeout(() => {
                    this.contactNextDealer();
                }, 2000);
            }
        }, 120000); // 2 minutes

        // Store timeout ID so we can clear it on success
        dealer.contactTimeoutId = timeoutId;

        try {
            await this.websocketClient.contactDealer(dealer, this.customerInfo);
        } catch (error) {
            console.error('[App] Error contacting dealer:', error);
            this.showNotification('error', 'Connection Error', error.message);
            // Reset status on error so retry is possible
            dealer.contactStatus = 'failed';
            this.contactInProgress = false;
            // Clear timeout since we're handling the failure
            if (dealer.contactTimeoutId) {
                clearTimeout(dealer.contactTimeoutId);
                delete dealer.contactTimeoutId;
            }
        }
    },

    async startContacting() {
        if (!this.websocketClient || !this.websocketClient.isConnected) {
            alert('Not connected to automation server. Please start the backend first.\n\nRun: cd backend && python websocket_server.py');
            return;
        }

        // Validate currentSearch exists
        if (!this.currentSearch || !this.currentSearch.dealerships) {
            alert('No search results available. Please perform a search first.');
            return;
        }

        const dealersToContact = this.currentSearch.dealerships
            .filter(d => d.selected && (d.contactStatus === 'pending' || d.contactStatus === 'failed'))
            .sort((a, b) => a.distanceMiles - b.distanceMiles);

        if (dealersToContact.length === 0) {
            alert('No dealerships selected for contacting');
            return;
        }

        const proceed = confirm(
            `Start contacting ${dealersToContact.length} dealerships?\n\n` +
            `This will use REAL automation (not simulation).\n\n` +
            `Order: Closest to furthest\n` +
            `Estimated time: ${dealersToContact.length * 60} seconds\n\n` +
            `Click OK to begin.`
        );

        if (!proceed) return;

        this.contactState = 'running';
        this.dealersToContact = dealersToContact;
        this.contactNextDealer();
    },

    contactNextDealer() {
        if (this.contactState !== 'running') {
            return;
        }

        // Don't start next if current still running (prevents race condition)
        if (this.contactInProgress) {
            console.warn('[Batch] Contact still in progress, waiting for completion...');
            return;
        }

        // Check WebSocket connection before proceeding
        if (!this.websocketClient || !this.websocketClient.isConnected) {
            this.stopContacting();
            alert('Lost connection to automation server. Batch processing stopped.\n\nPlease check the backend and restart.');
            this.showNotification('error', 'Connection Lost', 'Batch processing stopped due to disconnection');
            return;
        }

        // Find next pending dealer
        const nextDealer = this.dealersToContact.find(d =>
            d.contactStatus === 'pending' || d.contactStatus === 'failed'
        );

        if (!nextDealer) {
            // All done
            this.stopContacting();
            this.showNotification('success', 'Batch Complete', `Contacted ${this.dealersToContact.length} dealerships`);
            return;
        }

        // Mark as in progress before starting
        this.contactInProgress = true;

        // Contact this dealer
        this.contactSingleDealer(nextDealer);
    },

    stopContacting() {
        this.contactState = 'stopped';
        this.contactInProgress = false;  // CRITICAL: Reset flag

        // Clear timeout on current dealer
        if (this.currentDealer && this.currentDealer.contactTimeoutId) {
            clearTimeout(this.currentDealer.contactTimeoutId);
            delete this.currentDealer.contactTimeoutId;
        }

        // Clear timeouts on all dealers in queue
        if (this.dealersToContact) {
            this.dealersToContact.forEach(dealer => {
                if (dealer.contactTimeoutId) {
                    clearTimeout(dealer.contactTimeoutId);
                    delete dealer.contactTimeoutId;
                }
            });
        }

        this.currentDealer = null;
        this.dealersToContact = [];
        this.saveState();
    },

    // ========== Helper Methods ==========

    updateDealerStatus(dealerName, status, statusMessage) {
        if (!this.currentSearch) return;

        const dealer = this.currentSearch.dealerships.find(d => d.dealer_name === dealerName);
        if (!dealer) return;

        // Define status priority (higher = more final, prevents out-of-order updates)
        const statusPriority = {
            'pending': 0,
            'contacting': 1,
            'contacted': 10,  // Final success state
            'failed': 10      // Final failure state
        };

        const currentPriority = statusPriority[dealer.contactStatus] || 0;
        const newPriority = statusPriority[status] || 0;

        // Only update if new status has equal or higher priority
        if (newPriority >= currentPriority) {
            dealer.contactStatus = status;
            dealer.statusMessage = statusMessage;
            dealer.lastStatusUpdate = Date.now();
        } else {
            console.warn(`[Status] Ignoring lower-priority update for ${dealerName}: ${status} (current: ${dealer.contactStatus})`);
        }
    },

    updateDealerWithResult(dealerName, result) {
        if (!this.currentSearch) return;

        const dealer = this.currentSearch.dealerships.find(d => d.dealer_name === dealerName);
        if (!dealer) return;

        dealer.contactStatus = result.success ? 'contacted' : 'failed';
        dealer.lastContactedAt = new Date().toISOString();

        // Clear timeout since contact completed (success or failure)
        if (dealer.contactTimeoutId) {
            clearTimeout(dealer.contactTimeoutId);
            delete dealer.contactTimeoutId;
        }

        // Add to contact history
        if (!dealer.contactHistory) dealer.contactHistory = [];
        dealer.contactHistory.push({
            timestamp: new Date().toISOString(),
            success: result.success,
            details: result.details,
            method: 'automated_websocket',
            contact_url: result.contact_url,
            captcha_type: result.captcha_type,
            screenshots: result.screenshots
        });

        this.saveState();
    },

    showNotification(type, title, message) {
        // Simple console notification for now
        // Can be upgraded to toast notifications later
        const emoji = {
            'success': '✅',
            'error': '❌',
            'warning': '⚠️',
            'info': 'ℹ️'
        }[type] || 'ℹ️';

        console.log(`${emoji} ${title}: ${message}`);

        // Could add browser notification here
        // if (Notification.permission === 'granted') {
        //     new Notification(title, { body: message });
        // }
    },

    // ========== Screenshot Methods ==========

    getScreenshotUrl(screenshot) {
        if (screenshot.startsWith('http')) {
            return screenshot;
        }
        // Use same host and protocol as page is served from
        const protocol = window.location.protocol; // http: or https:
        const host = window.location.host; // includes port
        return `${protocol}//${host}/screenshots/${screenshot}`;
    },

    viewScreenshot(screenshot, dealer, attempt) {
        this.currentScreenshotUrl = this.getScreenshotUrl(screenshot);
        this.screenshotModalTitle = `${dealer.dealer_name} - ${attempt.success ? 'Success' : 'Failed'}`;
        this.currentScreenshotInfo = {
            dealer_name: dealer.dealer_name,
            contact_url: attempt.contact_url,
            captcha_type: attempt.captcha_type,
            reason: attempt.details
        };
        this.showScreenshotModal = true;
    },

    closeScreenshotModal() {
        this.showScreenshotModal = false;
        this.currentScreenshotUrl = null;
        this.currentScreenshotInfo = null;
    }
};

// Make methods available globally
window.websocketMethods = websocketMethods;
