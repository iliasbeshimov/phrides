// Main Vue application setup
console.log('[App] Starting app initialization...');
console.log('[App] Vue available:', typeof Vue);

try {
    const { createApp } = Vue;
    console.log('[App] createApp extracted');

const app = createApp({
    data() {
        return {
            // View Management
            currentView: 'search-list', // 'search-list' or 'search-details'

            // Data Sources
            masterDealerships: [],
            availableMakes: [],

            // Search Management
            savedSearches: [],
            currentSearch: null,
            searchParams: { title: '', make: '', distance: '100', customDistance: '' },

            // Customer Information
            customerInfo: {
                firstName: '',
                lastName: '',
                email: '',
                phone: '',
                zipcode: '',
                message: ''
            },

            // UI State
            editMode: true,
            contactState: 'stopped',
            contactInProgress: false, // Track if contact automation currently running
            contactNextTimer: null, // Track setTimeout for next dealer
            sortBy: 'distance',
            currentDealer: null,
            contactInterval: null,
            showHistory: {},

            // WebSocket Integration
            websocketClient: null,
            websocketStatus: 'disconnected', // 'disconnected', 'connecting', 'connected'

            // Screenshot Modal
            showScreenshotModal: false,
            currentScreenshotUrl: null,
            currentScreenshotInfo: null,
            screenshotModalTitle: '',

            // Templates
            messageTemplates: {
                lease: "Hi, I am interested in leasing a new SUV. Who do I need to talk to for what options are available? Best regards.",
                purchase: "Hello, I'm looking to purchase a new vehicle. What inventory do you currently have available? Thank you."
            }
        }
    },

    methods: {
        async loadInitialData() {
            // Google Sheets source (always up-to-date)
            const GOOGLE_SHEET_ID = '1rvZN95GJgmf3Jiv5LWUYJETPE42P1iZE88UTLV_J94k';
            const GOOGLE_SHEET_GID = '826403005';  // Master Production List tab
            const GOOGLE_SHEETS_URL = `https://docs.google.com/spreadsheets/d/${GOOGLE_SHEET_ID}/export?format=csv&gid=${GOOGLE_SHEET_GID}`;

            // Fallback sources (local CSV files)
            const sources = [
                { url: GOOGLE_SHEETS_URL, name: 'Google Sheets (Production)', isGoogleSheets: true },
                { url: './Dealerships.csv', name: 'Local CSV (Backup)', isGoogleSheets: false },
                { url: '../Dealerships.csv', name: 'Root CSV (Backup)', isGoogleSheets: false }
            ];

            for (const source of sources) {
                try {
                    console.log(`Attempting to load dealership data from: ${source.name}`);
                    const response = await fetch(source.url);
                    if (!response.ok) {
                        console.warn(`Failed to load ${source.name}: ${response.status}`);
                        continue;
                    }

                    const csvText = await response.text();
                    if (!csvText || csvText.trim().length === 0) {
                        console.warn(`Empty CSV file: ${source.name}`);
                        continue;
                    }

                    const parser = new CSVDataParser();
                    let dealerships = parser.parseCSV(csvText);

                    if (dealerships.length === 0) {
                        console.warn(`No dealerships parsed from: ${source.name}`);
                        continue;
                    }

                    // Normalize Google Sheets format to match expected format
                    if (source.isGoogleSheets) {
                        console.log('Normalizing Google Sheets data format...');
                        console.log('Sample raw data (first dealership):', dealerships[0]);
                        dealerships = dealerships.map(d => this.normalizeGoogleSheetsData(d));
                        console.log('Sample normalized data (first dealership):', dealerships[0]);
                    }

                    // Validate required fields (relaxed validation for Google Sheets)
                    const requiredFields = source.isGoogleSheets
                        ? ['dealer_name', 'website']  // Minimal requirements for Google Sheets
                        : ['dealer_name', 'website', 'latitude', 'longitude', 'zip_code'];

                    const invalidDealerships = dealerships.filter(d => {
                        return !requiredFields.every(field => d[field]);
                    });

                    if (invalidDealerships.length > 0) {
                        console.warn(`Found ${invalidDealerships.length} dealerships with missing required fields`);
                        // Filter out invalid entries
                        dealerships = dealerships.filter(d => {
                            return requiredFields.every(field => d[field]);
                        });
                    }

                    this.masterDealerships = dealerships;
                    this.applyContactPageOverridesToMaster();

                    const makeManager = new MakeManager(this.masterDealerships);
                    this.availableMakes = makeManager.availableMakes;

                    console.log(`✅ Successfully loaded ${this.masterDealerships.length} dealerships from ${source.name}`);
                    console.log(`Available makes: ${this.availableMakes.join(', ')}`);
                    return; // Success, exit the loop

                } catch (error) {
                    console.error(`Error loading ${source.name}:`, error);
                }
            }

            // If we get here, all attempts failed
            console.error("Failed to load dealership data from any source");
            alert("Could not load dealership data. Please check that the CSV file exists and is accessible.");
        },

        normalizeGoogleSheetsData(dealer) {
            /**
             * Normalize Google Sheets column format to match expected format.
             *
             * Master Production List columns: make, state, dealerName, address, phone, websiteLink,
             *                                 contactPagLink, inventoryLink, lat, long
             * Expected format: make, dealer_name, website, latitude, longitude, zip_code, city, state, etc.
             */

            // Extract zip code and city from address field
            // Address format: "Street Address City, ST, ZIP"
            const addressParts = this.parseAddress(dealer.address || '');

            return {
                // Basic info
                make: dealer.make || 'Unknown',  // Use make from sheet
                dealer_name: dealer.dealerName || dealer.dealer_name,
                state: dealer.state,
                city: addressParts.city || '',
                zip_code: addressParts.zip || '',
                address_line1: addressParts.street || dealer.address,
                address_line2: '',
                full_address: dealer.address,

                // Contact info
                phone: dealer.phone,
                website: dealer.websiteLink || dealer.website,
                email: dealer.email || '',

                // URLs
                inventory_link: dealer.inventoryLink || '',
                service_link: dealer.serviceLink || '',
                contact_page_link: dealer.contactPagLink || dealer.contactPageLink || '',  // Note: typo in sheet (contactPagLink)

                // Geographic coordinates
                latitude: parseFloat(dealer.lat || dealer.latitude) || null,
                longitude: parseFloat(dealer.long || dealer.longitude) || null,

                // Additional fields
                country: 'USA',
                has_quote: dealer.has_quote || 'N',
                sales_available: 'Y',
                service_available: dealer.serviceLink ? 'Y' : 'N',
                parts_available: 'Y',

                // Source tracking
                data_source: 'google_sheets',
                last_updated: new Date().toISOString()
            };
        },

        parseAddress(addressString) {
            /**
             * Parse address string to extract street, city, state, zip.
             * Expected format: "Street Address City, ST, ZIP"
             * Examples:
             *   "3060 Dauphin Street Mobile, AL, 36606"
             *   "217 Eastern Blvd. Montgomery, AL, 36124"
             */
            const result = {
                street: '',
                city: '',
                state: '',
                zip: ''
            };

            if (!addressString) return result;

            // Match pattern: "Street City, ST, ZIP"
            const pattern = /^(.+?)\s+([A-Za-z\s]+),\s*([A-Z]{2}),?\s*(\d{5}(?:-\d{4})?)$/;
            const match = addressString.match(pattern);

            if (match) {
                result.street = match[1].trim();
                result.city = match[2].trim();
                result.state = match[3].trim();
                result.zip = match[4].trim();
            } else {
                // Fallback: try to extract zip code at least
                const zipMatch = addressString.match(/\b(\d{5}(?:-\d{4})?)\b/);
                if (zipMatch) {
                    result.zip = zipMatch[1];
                }
                result.street = addressString;
            }

            return result;
        },

        async saveState() {
            try {
                // Save to localStorage for immediate use
                localStorage.setItem('dealership_app_state', JSON.stringify({
                    currentView: this.currentView,
                    currentSearch: this.currentSearch,
                    customerInfo: this.customerInfo,
                    searchParams: this.searchParams
                }));

                // Save to persistent server storage
                await this.saveStateToServer();
                await this.saveSavedSearches();
            } catch (e) {
                console.error("Error saving state:", e);
            }
        },
        async loadState() {
            try {
                // Try loading from server first, fallback to localStorage
                await this.loadStateFromServer();
                await this.loadSavedSearches();

                if (this.currentSearch && Array.isArray(this.currentSearch.dealerships)) {
                    this.applyContactOverridesToDealers(this.currentSearch.dealerships);
                }

                if (Array.isArray(this.savedSearches)) {
                    this.savedSearches.forEach(search => {
                        if (search && Array.isArray(search.dealerships)) {
                            this.applyContactOverridesToDealers(search.dealerships);
                        }
                    });
                }
            } catch (e) {
                console.error("Error loading state:", e);
                // Fallback to localStorage
                try {
                    const savedState = localStorage.getItem('dealership_app_state');
                    if (savedState) {
                        const state = JSON.parse(savedState);
                        this.currentView = state.currentView || 'search-list';
                        this.currentSearch = state.currentSearch;
                        this.customerInfo = state.customerInfo || {
                            firstName: 'Ilias',
                            lastName: 'Beshimov',
                            email: 'ilias.beshimov@gmail.com',
                            phone: '415-340-4828',
                            zipcode: '',
                            message: ''
                        };
                        this.searchParams = state.searchParams || { title: '', make: '', distance: '100', customDistance: '' };

                        if (this.currentSearch && Array.isArray(this.currentSearch.dealerships)) {
                            this.applyContactOverridesToDealers(this.currentSearch.dealerships);
                        }
                    }
                } catch (localError) {
                    console.error("Error loading from localStorage:", localError);
                }
            }
        },
        async saveSavedSearches() {
            try {
                console.log('💾 Saving searches:', this.savedSearches.length, 'searches');

                // Save to localStorage for immediate use
                localStorage.setItem('saved_searches', JSON.stringify(this.savedSearches));

                // Save to persistent server storage
                await this.saveSearchesToServer();
            } catch (e) {
                console.error("Error saving searches:", e);
            }
        },
        async loadSavedSearches() {
            try {
                // Try loading from server first
                await this.loadSearchesFromServer();
            } catch (e) {
                console.error("Error loading searches from server:", e);
                // Fallback to localStorage
                try {
                    const savedSearches = localStorage.getItem('saved_searches');
                    if (savedSearches) {
                        this.savedSearches = JSON.parse(savedSearches);
                        console.log(`📖 Loaded ${this.savedSearches.length} saved searches from localStorage`);
                        this.savedSearches.forEach(search => {
                            if (search && Array.isArray(search.dealerships)) {
                                this.applyContactOverridesToDealers(search.dealerships);
                            }
                        });
                    } else {
                        console.log('No saved searches found in localStorage');
                        this.savedSearches = [];
                    }
                } catch (localError) {
                    console.error("Error loading searches from localStorage:", localError);
                    this.savedSearches = [];
                }
            }
        },

        updateSearch() {
            // Validate inputs
            if (!this.searchParams.title || this.searchParams.title.trim() === '') {
                alert('Please enter a search title.');
                return;
            }
            const userZip = this.customerInfo.zipcode;
            if (!userZip || !zipCoordinates[userZip]) {
                alert('Please enter a valid US zip code.');
                return;
            }
            if (!this.searchParams.make) {
                alert('Please select a vehicle make.');
                return;
            }

            // Handle custom distance
            let radiusMiles;
            if (this.searchParams.distance === 'other') {
                if (!this.searchParams.customDistance || isNaN(this.searchParams.customDistance)) {
                    alert('Please enter a valid custom distance.');
                    return;
                }
                radiusMiles = parseFloat(this.searchParams.customDistance);
            } else {
                radiusMiles = parseFloat(this.searchParams.distance);
            }

            const userCoords = zipCoordinates[userZip];
            const targetMake = this.searchParams.make;

            // Find all dealerships matching the current criteria
            let foundDealerships = this.masterDealerships
                .filter(dealer => dealer.make === targetMake)
                .map(dealer => {
                    const dealerCoords = { lat: dealer.latitude, lon: dealer.longitude };
                    const distance = this.haversineDistance(userCoords, dealerCoords);
                    return { ...dealer, distanceMiles: Math.round(distance * 10) / 10 };
                })
                .filter(dealer => dealer.distanceMiles <= radiusMiles);

            if (foundDealerships.length === 0) {
                alert(`No ${targetMake} dealerships found within ${radiusMiles} miles of ${userZip}`);
                return;
            }

            // SAFE EXPAND-ONLY LOGIC: Always preserve existing contact history
            const existingIds = this.currentSearch ? new Set(this.currentSearch.dealerships.map(d => d.id)) : new Set();
            const newDealerships = foundDealerships.filter(d => !existingIds.has(d.id));
            const existingDealerships = this.currentSearch ? this.currentSearch.dealerships : [];

            // Log expansion details for transparency
            console.log(`🔍 Search Expansion Details:`);
            console.log(`  - Existing dealerships: ${existingDealerships.length}`);
            console.log(`  - New dealerships found: ${newDealerships.length}`);
            console.log(`  - Total after expansion: ${existingDealerships.length + newDealerships.length}`);

            // Show expansion preview if adding many dealerships
            if (newDealerships.length > 10) {
                const proceed = confirm(
                    `This search will add ${newDealerships.length} new dealerships to your existing ${existingDealerships.length}.\n\n` +
                    `Total dealerships: ${existingDealerships.length + newDealerships.length}\n\n` +
                    `✅ All existing contact history will be preserved.\n\n` +
                    `Do you want to proceed?`
                );
                if (!proceed) {
                    return; // User cancelled
                }
            }

            // Create or update search with SAFE EXPANSION
            const searchId = this.currentSearch ? this.currentSearch.id : `search_${Date.now()}`;
            const isNewSearch = !this.currentSearch;

            // Update the search object with new parameters
            this.currentSearch = {
                id: searchId,
                name: this.searchParams.title.trim(),
                parameters: {
                    ...this.searchParams,
                    title: this.searchParams.title.trim(),
                    zipcode: userZip
                },
                dealerships: [...existingDealerships, ...newDealerships]
                    .sort((a, b) => a.distanceMiles - b.distanceMiles)  // Sort closest first (was reversed)
                    .map((dealer, index) => {
                        // Ensure all required properties exist, but preserve existing status
                        return {
                            ...dealer,
                            id: dealer.id || `dealer_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
                            contactStatus: dealer.contactStatus || 'pending',
                            selected: dealer.selected !== undefined ? dealer.selected : true,
                            contactHistory: dealer.contactHistory || [],
                            addedAt: dealer.addedAt || new Date().toISOString(),
                            contact_page_link: dealer.contact_page_link || dealer.contactPageLink || dealer.contactPagLink || (dealer.website ? this.getContactPageUrl(dealer.website) : ''),
                            contactPagLink: dealer.contactPagLink || dealer.contact_page_link || '',
                            contactPageLink: dealer.contactPageLink || dealer.contact_page_link || ''
                        };
                    }),
                createdAt: isNewSearch ? new Date().toISOString() : this.currentSearch.createdAt,
                lastExpanded: new Date().toISOString()
            };

            // Exit edit mode after successful update
            this.editMode = false;

            console.log('=== UPDATE SEARCH DEBUG ===');
            console.log('Created search:', this.currentSearch.name);
            console.log('Search ID:', this.currentSearch.id);
            console.log('Dealerships count:', this.currentSearch.dealerships.length);

            // Save to searches list immediately
            this.saveSearchToList();

            // Show success message
            const message = existingDealerships.length > 0 ?
                `✅ Search expanded! Added ${newDealerships.length} new dealerships. All existing contact history preserved.` :
                `✅ Search "${this.currentSearch.name}" created! Found ${newDealerships.length} dealerships.`;

            console.log(message);
            alert(message); // Show user confirmation

            this.saveState();

            // Auto-save backup after search expansion
            this.createAutomaticBackup('search_expansion');
        },
        startContacting() {
            // Safety checks
            if (!this.currentSearch) {
                alert('No search available. Please create a search first.');
                return;
            }
            if (this.contactState === 'running') {
                console.warn('Contact process is already running');
                return;
            }

            const dealersToContact = this.currentSearch.dealerships
                .filter(d => d.selected && (d.contactStatus === 'pending' || d.contactStatus === 'failed'))
                .sort((a, b) => a.distanceMiles - b.distanceMiles); // Closest first (fixed)

            if (dealersToContact.length === 0) {
                alert('No dealerships selected for contacting. Please select at least one dealership.');
                this.contactState = 'stopped';
                return;
            }

            // Confirmation before starting
            const proceed = confirm(
                `🚀 Ready to start contacting ${dealersToContact.length} dealerships?\n\n` +
                `Contact order: Closest to furthest\n` +
                `Estimated time: ${dealersToContact.length * 2} seconds\n\n` +
                `Click OK to begin the contact process.`
            );

            if (!proceed) {
                return;
            }

            // Create backup before starting
            this.createAutomaticBackup('before_contact_start');

            console.log(`🚀 Starting contact process for ${dealersToContact.length} dealerships`);
            this.contactState = 'running';
            let dealerIndex = 0;

            this.contactInterval = setInterval(() => {
                if (dealerIndex >= dealersToContact.length) {
                    this.stopContacting();
                    return;
                }

                const dealer = dealersToContact[dealerIndex];
                this.currentDealer = dealer;
                console.log(`🏢 Contacting: ${dealer.dealer_name} (${dealer.distanceMiles} miles)`);

                const mainDealer = this.currentSearch.dealerships.find(d => d.id === dealer.id);
                if (mainDealer) {
                    // TODO: Replace with real automation call
                    // const success = await callPythonAutomation(dealer.website, this.customerInfo);
                    const success = Math.random() > 0.15; // 85% success rate simulation

                    mainDealer.contactStatus = success ? 'contacted' : 'failed';
                    mainDealer.lastContactedAt = new Date().toISOString();

                    // Add to contact history
                    if (!mainDealer.contactHistory) mainDealer.contactHistory = [];
                    mainDealer.contactHistory.push({
                        timestamp: new Date().toISOString(),
                        success: success,
                        details: success ? 'Form submitted successfully (simulated)' : 'Form submission failed (simulated)',
                        method: 'automated'
                    });

                    console.log(`  ${success ? '✅ Success' : '❌ Failed'}: ${dealer.dealer_name}`);
                }

                this.saveState();
                dealerIndex++;
            }, 2000);
        },
        stopContacting() {
            clearInterval(this.contactInterval);
            this.contactState = 'stopped';

            const completedCount = this.currentSearch ?
                this.currentSearch.dealerships.filter(d => ['contacted', 'failed', 'manual'].includes(d.contactStatus)).length : 0;

            console.log(`⏹️ Contact process stopped. Completed: ${completedCount} dealerships`);

            if (this.currentDealer) {
                console.log(`Last dealer contacted: ${this.currentDealer.dealer_name}`);
            }

            this.currentDealer = null;
            this.saveState();

            // Create backup after stopping
            this.createAutomaticBackup('after_contact_stop');
        },

        haversineDistance(coords1, coords2) {
            const toRad = (x) => x * Math.PI / 180;
            const R = 3959; // Earth's radius in miles
            const dLat = toRad(coords2.lat - coords1.lat);
            const dLon = toRad(coords2.lon - coords1.lon);
            const lat1 = toRad(coords1.lat);
            const lat2 = toRad(coords2.lat);
            const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            const straightLineDistance = R * c;

            // Apply driving distance multiplier (roads aren't straight lines)
            // Multiplier varies by distance: shorter = less deviation, longer = more deviation
            let drivingMultiplier;
            if (straightLineDistance < 50) {
                drivingMultiplier = 1.15; // 15% longer for short distances
            } else if (straightLineDistance < 200) {
                drivingMultiplier = 1.25; // 25% longer for medium distances
            } else {
                drivingMultiplier = 1.35; // 35% longer for long distances
            }

            return straightLineDistance * drivingMultiplier;
        },

        // Bulk Selection Methods
        selectAll() {
            if (!this.currentSearch) return;
            this.currentSearch.dealerships.forEach(dealer => {
                dealer.selected = true;
            });
            this.saveState();
        },
        selectNone() {
            if (!this.currentSearch) return;
            this.currentSearch.dealerships.forEach(dealer => {
                dealer.selected = false;
            });
            this.saveState();
        },
        selectPending() {
            if (!this.currentSearch) return;
            this.currentSearch.dealerships.forEach(dealer => {
                dealer.selected = dealer.contactStatus === 'pending';
            });
            this.saveState();
        },
        /**
         * Select only dealerships where contact attempts failed.
         * Includes both 'failed' (automation error) and 'manual' (CAPTCHA/intervention needed).
         * Use case: Quick retry workflow after initial contact batch.
         * Added: Oct 31, 2024
         */
        selectFailed() {
            if (!this.currentSearch) return;
            this.currentSearch.dealerships.forEach(dealer => {
                dealer.selected = dealer.contactStatus === 'failed' || dealer.contactStatus === 'manual';
            });
            this.saveState();
        },

        // Sorting Methods
        sortDealerships() {
            if (!this.currentSearch) return;
            const dealers = this.currentSearch.dealerships;

            switch(this.sortBy) {
                case 'distance':
                    dealers.sort((a, b) => a.distanceMiles - b.distanceMiles);
                    break;
                case 'name':
                    dealers.sort((a, b) => a.dealer_name.localeCompare(b.dealer_name));
                    break;
                case 'status':
                    dealers.sort((a, b) => a.contactStatus.localeCompare(b.contactStatus));
                    break;
            }
            this.saveState();
        },

        // Contact Order and Status
        getContactOrder(dealer) {
            if (!this.currentSearch || !dealer.selected) return '';
            const selectedDealers = this.currentSearch.dealerships
                .filter(d => d.selected)
                .sort((a, b) => b.distanceMiles - a.distanceMiles); // Furthest first
            return selectedDealers.findIndex(d => d.id === dealer.id) + 1;
        },
        getStatusIcon(status) {
            const icons = {
                'pending': '⏳',
                'contacted': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'manual': '✋'
            };
            return icons[status] || '❓';
        },
        getStatusDisplay() {
            const displays = {
                'stopped': '⏹️ Stopped',
                'running': '▶️ Running'
            };
            return displays[this.contactState] || '❓ Unknown';
        },

        // Individual Contact Actions
        // NOTE: contactSingleDealer is now defined in websocket_integration.js
        // This simulation version has been removed to use real WebSocket automation
        retryContact(dealer) {
            if (!dealer) return;
            console.log(`Retrying contact for dealer: ${dealer.dealer_name}`);
            dealer.contactStatus = 'pending';
            dealer.manualRequired = false;
            this.saveState();
        },
        showManualOptions(dealer) {
            // Deprecated in UI, keep for compatibility
            this.openManualContact(dealer);
        },
        skipDealer(dealer) {
            if (!dealer) return;
            console.log(`Skipping dealer: ${dealer.dealer_name}`);
            dealer.contactStatus = 'skipped';
            dealer.selected = false;
            this.saveState();
        },

        getDealerContactUrl(dealer) {
            if (!dealer) return '';
            return dealer.contact_page_link || dealer.contactPageLink || dealer.contactPagLink || (dealer.website ? this.getContactPageUrl(dealer.website) : '');
        },
        markManualContactSuccess(dealer) {
            if (!dealer) return;
            if (dealer.contactStatus === 'contacted') {
                this.showNotification('info', 'Already Contacted', `${dealer.dealer_name} is already marked as contacted.`);
                return;
            }
            dealer.contactStatus = 'contacted';
            dealer.manualRequired = false;
            dealer.lastContactedAt = new Date().toISOString();

            if (!dealer.contactHistory) dealer.contactHistory = [];
            dealer.contactHistory.push({
                timestamp: new Date().toISOString(),
                success: true,
                details: 'Manually contacted',
                method: 'manual',
                contact_url: this.getDealerContactUrl(dealer),
                screenshots: []
            });

            this.showNotification('success', `Manual Contact Saved`, `${dealer.dealer_name} marked as contacted manually.`);
            this.saveState();
        },
        openManualContact(dealer, url) {
            const finalUrl = url || this.getDealerContactUrl(dealer);
            if (finalUrl) {
                window.open(finalUrl, '_blank', 'noopener');
            }

            const payload = this.buildPrefillPayload(dealer);
            if (payload) {
                navigator.clipboard.writeText(payload).then(() => {
                    this.showNotification('info', 'Prefill Copied', 'Contact details copied to clipboard for quick paste.');
                }).catch(() => {
                    console.warn('Clipboard write failed');
                });
            }
        },
        buildPrefillPayload(dealer) {
            if (!dealer) return '';
            const fields = {
                firstName: this.customerInfo.firstName,
                lastName: this.customerInfo.lastName,
                email: this.customerInfo.email,
                phone: this.customerInfo.phone,
                message: this.customerInfo.message,
                dealership: dealer.dealer_name,
                contactUrl: this.getDealerContactUrl(dealer)
            };
            return Object.entries(fields)
                .filter(([, value]) => value)
                .map(([key, value]) => `${key}: ${value}`)
                .join('\n');
        },
        editContactPageUrl(dealer) {
            if (!dealer) return;
            dealer.editingContactUrl = true;
            dealer.tempContactUrl = this.getDealerContactUrl(dealer) || '';
        },
        cancelContactPageEdit(dealer) {
            if (!dealer) return;
            dealer.editingContactUrl = false;
            delete dealer.tempContactUrl;
        },
        saveContactPageUrl(dealer) {
            if (!dealer || !dealer.editingContactUrl) return;
            const url = (dealer.tempContactUrl || '').trim();
            if (url) {
                this.updateContactPageLink(dealer, url, 'manual_edit');
            }
            dealer.editingContactUrl = false;
            delete dealer.tempContactUrl;
        },
        updateContactPageLink(dealer, url, source = 'automated', persist = true) {
            if (!dealer || !url) return;

            dealer.contact_page_link = url;
            dealer.contactPagLink = url;
            dealer.contactPageLink = url;
            dealer.contact_url_source = source;

            const masterList = Array.isArray(this.masterDealerships) ? this.masterDealerships : [];
            const master = masterList.find(d => {
                if (!d) return false;
                if (d.dealer_name && dealer.dealer_name && d.dealer_name.toLowerCase() === dealer.dealer_name.toLowerCase()) {
                    if (d.website && dealer.website) {
                        return d.website.toLowerCase() === dealer.website.toLowerCase();
                    }
                    return true;
                }
                return false;
            });

            if (master) {
                master.contact_page_link = url;
                master.contactPagLink = url;
                master.contactPageLink = url;
            }

            let baseUrl = '';
            try {
                const parsed = new URL(url);
                baseUrl = parsed.origin + '/';
            } catch (error) {
                baseUrl = '';
            }

            if (baseUrl) {
                this.updateWebsiteLinkInternal(dealer, baseUrl, false);
            }

            const overrideKey = this.getContactOverrideKey(dealer);
            if (overrideKey) {
                const overrides = this.loadContactPageOverrides();
                const existing = overrides[overrideKey] && typeof overrides[overrideKey] === 'object' ? overrides[overrideKey] : {};
                overrides[overrideKey] = {
                    ...existing,
                    url,
                    dealerName: dealer.dealer_name,
                    updatedAt: new Date().toISOString(),
                    website: dealer.website || existing.website || ''
                };
                localStorage.setItem('contact_page_overrides', JSON.stringify(overrides));
            }

            if (persist) {
                this.saveState();
            }
        },
        updateWebsiteLinkInternal(dealer, baseUrl, persist = true) {
            if (!dealer || !baseUrl) return;

            dealer.website = baseUrl;
            dealer.websiteLink = baseUrl;

            const masterList = Array.isArray(this.masterDealerships) ? this.masterDealerships : [];
            const master = masterList.find(d => {
                if (!d) return false;
                if (d.dealer_name && dealer.dealer_name && d.dealer_name.toLowerCase() === dealer.dealer_name.toLowerCase()) {
                    return true;
                }
                return false;
            });

            if (master) {
                master.website = baseUrl;
                master.websiteLink = baseUrl;
            }

            const overrideKey = this.getContactOverrideKey(dealer);
            if (overrideKey) {
                const overrides = this.loadContactPageOverrides();
                const existing = overrides[overrideKey] && typeof overrides[overrideKey] === 'object' ? overrides[overrideKey] : {};
                overrides[overrideKey] = {
                    ...existing,
                    website: baseUrl,
                    dealerName: dealer.dealer_name,
                    updatedAt: new Date().toISOString()
                };
                localStorage.setItem('contact_page_overrides', JSON.stringify(overrides));
            }

            if (persist) {
                this.saveState();
            }
        },
        getContactOverrideKey(dealer) {
            if (!dealer) return null;
            if (dealer.id) return dealer.id;
            if (dealer.dealer_name) return dealer.dealer_name.toLowerCase();
            return null;
        },
        loadContactPageOverrides() {
            try {
                const raw = localStorage.getItem('contact_page_overrides');
                if (!raw) return {};
                const parsed = JSON.parse(raw);
                return parsed && typeof parsed === 'object' ? parsed : {};
            } catch (error) {
                console.error('Failed to load contact page overrides:', error);
                return {};
            }
        },
        applyContactPageOverridesToMaster() {
            if (!Array.isArray(this.masterDealerships) || this.masterDealerships.length === 0) return;
            const overrides = this.loadContactPageOverrides();
            if (!Object.keys(overrides).length) return;

            this.masterDealerships.forEach(dealer => {
                const key = this.getContactOverrideKey(dealer);
                if (!key || !overrides[key]) return;
                const data = overrides[key];
                const url = typeof data === 'string' ? data : data.url;
                if (url) {
                    dealer.contact_page_link = url;
                    dealer.contactPagLink = url;
                    dealer.contactPageLink = url;
                }
                if (data && data.website) {
                    dealer.website = data.website;
                    dealer.websiteLink = data.website;
                }
            });
        },
        applyContactOverridesToDealers(dealers) {
            if (!Array.isArray(dealers) || dealers.length === 0) return;
            const overrides = this.loadContactPageOverrides();
            if (!Object.keys(overrides).length) return;

            dealers.forEach(dealer => {
                const key = this.getContactOverrideKey(dealer);
                if (!key || !overrides[key]) return;
                const data = overrides[key];
                const url = typeof data === 'string' ? data : data.url;
                if (url) {
                    dealer.contact_page_link = url;
                    dealer.contactPagLink = url;
                    dealer.contactPageLink = url;
                }
                if (data && data.website) {
                    dealer.website = data.website;
                    dealer.websiteLink = data.website;
                }
            });
        },

        // Message Templates
        applyMessageTemplate(event) {
            const templateKey = event.target.value;
            if (templateKey && this.messageTemplates[templateKey]) {
                this.customerInfo.message = this.messageTemplates[templateKey];
                this.saveState();
            }
            event.target.value = ''; // Reset dropdown
        },

        // Retry Failed Contacts
        retryFailedContacts() {
            if (!this.currentSearch) return;
            console.log('Retrying all failed/manual contacts');
            this.currentSearch.dealerships
                .filter(d => d.contactStatus === 'failed' || d.contactStatus === 'manual')
                .forEach(dealer => {
                    dealer.contactStatus = 'pending';
                    dealer.selected = true;
                    dealer.manualRequired = false;
                });
            this.saveState();
        },

        // Export and Backup
        exportResults() {
            if (!this.currentSearch) {
                alert('No search results to export');
                return;
            }

            const exportData = {
                searchName: this.currentSearch.name,
                parameters: this.currentSearch.parameters,
                dealerships: this.currentSearch.dealerships,
                summary: {
                    total: this.totalDealerships,
                    contacted: this.successCount,
                    failed: this.failedCount,
                    pending: this.pendingCount,
                    successRate: this.successRate
                },
                exportedAt: new Date().toISOString()
            };

            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `dealership-results-${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            console.log('Results exported successfully');
        },
        createBackup() {
            const backupData = {
                version: '1.0',
                timestamp: new Date().toISOString(),
                currentSearch: this.currentSearch,
                customerInfo: this.customerInfo,
                searchParams: this.searchParams,
                reason: 'manual_backup'
            };

            const backupKey = `backup_${Date.now()}`;
            localStorage.setItem(backupKey, JSON.stringify(backupData));

            // Keep only last 5 backups
            this.cleanOldBackups();

            alert(`Backup created successfully: ${backupKey}`);
            console.log('Backup created:', backupKey);
        },
        createAutomaticBackup(reason = 'automatic') {
            const backupData = {
                version: '1.0',
                timestamp: new Date().toISOString(),
                currentSearch: this.currentSearch,
                customerInfo: this.customerInfo,
                searchParams: this.searchParams,
                reason: reason
            };

            const backupKey = `auto_backup_${Date.now()}`;
            localStorage.setItem(backupKey, JSON.stringify(backupData));
            console.log(`Automatic backup created: ${backupKey} (reason: ${reason})`);

            // Keep only last 10 automatic backups
            this.cleanOldBackups();
        },
        cleanOldBackups() {
            const allBackupKeys = Object.keys(localStorage)
                .filter(key => key.startsWith('backup_') || key.startsWith('auto_backup_'))
                .sort();

            // Keep last 5 manual backups + last 10 automatic backups
            const manualBackups = allBackupKeys.filter(key => key.startsWith('backup_'));
            const autoBackups = allBackupKeys.filter(key => key.startsWith('auto_backup_'));

            if (manualBackups.length > 5) {
                manualBackups.slice(0, -5).forEach(key => localStorage.removeItem(key));
            }
            if (autoBackups.length > 10) {
                autoBackups.slice(0, -10).forEach(key => localStorage.removeItem(key));
            }
        },

        // Search List Management
        refreshSearchList() {
            console.log('=== MANUAL REFRESH ===');
            this.loadSavedSearches();
            console.log('After refresh - saved searches:', this.savedSearches.length);
        },
        startNewSearch() {
            // Reset for new search
            this.currentSearch = null;
            this.searchParams = { title: '', make: '', distance: '100', customDistance: '' };
            this.customerInfo.zipcode = '';
            this.editMode = true;
            this.currentView = 'search-details';
            console.log('Starting new search - switched to details view');
            this.saveState();
        },
        openSearch(search) {
            this.currentSearch = search;
            this.searchParams = { ...search.parameters };
            // Ensure title is loaded from the search name
            this.searchParams.title = search.name;
            this.customerInfo.zipcode = search.parameters.zipcode;
            this.editMode = false;
            this.currentView = 'search-details';
            console.log(`Opened search: ${search.name}`);
            console.log('Loaded search params:', this.searchParams);
            this.saveState();
        },
        backToSearchList() {
            console.log('=== BACK TO SEARCH LIST DEBUG ===');
            console.log('Current search exists:', !!this.currentSearch);

            // Check if we have enough info to create a basic search
            if (this.searchParams.title && this.searchParams.title.trim() !== '') {
                if (!this.currentSearch) {
                    // Create a basic search if one doesn't exist but we have a title
                    console.log('Creating basic search from title:', this.searchParams.title);
                    this.currentSearch = {
                        id: `search_${Date.now()}`,
                        name: this.searchParams.title.trim(),
                        parameters: { ...this.searchParams },
                        dealerships: [],
                        createdAt: new Date().toISOString(),
                        lastExpanded: new Date().toISOString()
                    };
                }
            }

            if (this.currentSearch) {
                console.log('Current search name:', this.currentSearch.name);
                console.log('Current search ID:', this.currentSearch.id);
                console.log('Current search dealerships count:', this.currentSearch.dealerships ? this.currentSearch.dealerships.length : 0);
                this.saveSearchToList();
            } else {
                console.log('No search to save');
            }

            this.currentView = 'search-list';
            console.log('Saved searches count:', this.savedSearches.length);
            console.log('All saved searches:', this.savedSearches.map(s => s.name));
            this.saveState();
        },
        saveSearchToList() {
            console.log('=== SAVE SEARCH TO LIST DEBUG ===');
            if (!this.currentSearch) {
                console.log('ERROR: No current search to save');
                return;
            }

            console.log('Saving search:', this.currentSearch.name);
            console.log('Search ID:', this.currentSearch.id);
            console.log('Search parameters:', this.currentSearch.parameters);
            console.log('Search has dealerships:', !!this.currentSearch.dealerships);

            // Create a clean copy of the current search
            const searchToSave = {
                ...this.currentSearch,
                name: this.currentSearch.name,
                parameters: { ...this.currentSearch.parameters }
            };

            const existingIndex = this.savedSearches.findIndex(s => s.id === this.currentSearch.id);
            console.log('Existing search index:', existingIndex);

            if (existingIndex >= 0) {
                // Update existing search completely
                this.savedSearches[existingIndex] = searchToSave;
                console.log(`Updated existing search: ${searchToSave.name}`);
                console.log('Updated search parameters:', this.savedSearches[existingIndex].parameters);
            } else {
                // Add new search
                this.savedSearches.push(searchToSave);
                console.log(`Added new search to list: ${searchToSave.name}`);
            }

            console.log('Saved searches before save:', this.savedSearches.length);
            this.saveSavedSearches();
            console.log('Saved searches after save:', this.savedSearches.length);
        },
        duplicateSearch(search) {
            const duplicatedSearch = {
                ...search,
                id: `search_${Date.now()}`,
                name: `${search.name} (Copy)`,
                parameters: {
                    ...search.parameters,
                    title: `${search.parameters.title} (Copy)`
                },
                createdAt: new Date().toISOString(),
                lastExpanded: new Date().toISOString(),
                dealerships: search.dealerships.map(dealer => ({
                    ...dealer,
                    contactStatus: 'pending',
                    contactHistory: [],
                    selected: true
                }))
            };
            this.savedSearches.push(duplicatedSearch);
            this.saveSavedSearches();
            console.log(`Search duplicated: ${duplicatedSearch.name}`);
        },
        deleteSearch(searchId) {
            const search = this.savedSearches.find(s => s.id === searchId);
            if (!search) return;

            const confirmed = confirm(`Are you sure you want to delete "${search.name}"?\n\nThis action cannot be undone.`);
            if (confirmed) {
                this.savedSearches = this.savedSearches.filter(s => s.id !== searchId);
                if (this.currentSearch && this.currentSearch.id === searchId) {
                    this.currentSearch = null;
                    this.currentView = 'search-list';
                }
                this.saveSavedSearches();
                this.saveState();
                console.log(`Search deleted: ${search.name}`);
            }
        },
        exportSearch(search) {
            const exportData = {
                searchName: search.name,
                parameters: search.parameters,
                dealerships: search.dealerships,
                summary: {
                    total: search.dealerships.length,
                    contacted: this.getSearchSuccessCount(search),
                    failed: this.getSearchFailedCount(search),
                    pending: this.getSearchPendingCount(search),
                    successRate: this.getSearchProgress(search)
                },
                exportedAt: new Date().toISOString()
            };

            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${search.name.replace(/[^a-z0-9]/gi, '_').toLowerCase()}-${Date.now()}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            console.log(`Search exported: ${search.name}`);
        },

        // Search Statistics
        getSearchSuccessCount(search) {
            if (!search || !search.dealerships) return 0;
            return search.dealerships.filter(d => d.contactStatus === 'contacted').length;
        },
        getSearchFailedCount(search) {
            if (!search || !search.dealerships) return 0;
            return search.dealerships.filter(d => d.contactStatus === 'failed' || d.contactStatus === 'manual').length;
        },
        getSearchPendingCount(search) {
            if (!search || !search.dealerships) return 0;
            return search.dealerships.filter(d => d.contactStatus === 'pending').length;
        },
        getSearchProgress(search) {
            if (!search || !search.dealerships || search.dealerships.length === 0) return 0;
            const contacted = this.getSearchSuccessCount(search);
            const failed = this.getSearchFailedCount(search);
            const attempted = contacted + failed;
            if (attempted === 0) return 0;
            return Math.round((contacted / attempted) * 100);
        },

        // History Management
        toggleHistory(dealerId) {
            this.showHistory[dealerId] = !this.showHistory[dealerId];
        },

        // Custom Distance Handling
        handleDistanceChange() {
            // Reset custom distance when switching away from 'other'
            if (this.searchParams.distance !== 'other') {
                this.searchParams.customDistance = '';
            }
        },

        // Website URL Handling
        getContactPageUrl(website) {
            if (!website) return '';

            // Clean up the website URL
            let baseUrl = website;
            if (!baseUrl.startsWith('http')) {
                baseUrl = 'https://' + baseUrl;
            }

            // Try to convert to contact page
            try {
                const url = new URL(baseUrl);
                const contactUrl = `${url.protocol}//${url.hostname}/contact`;
                return contactUrl;
            } catch (e) {
                // If URL parsing fails, return original
                return baseUrl;
            }
        },

        // Utility Methods
        formatTime(timestamp) {
            if (!timestamp) return '';
            return new Date(timestamp).toLocaleTimeString();
        },
        formatDate(timestamp) {
            if (!timestamp) return 'Never';
            const date = new Date(timestamp);
            const now = new Date();
            const diffTime = Math.abs(now - date);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

            if (diffDays === 1) {
                return 'Today';
            } else if (diffDays === 2) {
                return 'Yesterday';
            } else if (diffDays <= 7) {
                return `${diffDays - 1} days ago`;
            } else {
                return date.toLocaleDateString();
            }
        },
        formatDateTime(timestamp) {
            if (!timestamp) return 'Unknown';
            const date = new Date(timestamp);

            // Convert to PST (UTC-8) or PDT (UTC-7) depending on daylight saving
            const pstDate = new Date(date.toLocaleString("en-US", {timeZone: "America/Los_Angeles"}));

            // Format as MM/DD/YY H:MM AM/PM
            const month = (pstDate.getMonth() + 1).toString();
            const day = pstDate.getDate().toString();
            const year = pstDate.getFullYear().toString().slice(-2);

            let hours = pstDate.getHours();
            const minutes = pstDate.getMinutes().toString().padStart(2, '0');
            const ampm = hours >= 12 ? 'PM' : 'AM';
            hours = hours % 12;
            hours = hours ? hours : 12; // 0 should be 12

            return `${month}/${day}/${year} ${hours}:${minutes} ${ampm}`;
        },
        toggleEditMode() {
            // Safety check: warn if contacting is in progress
            if (!this.editMode && this.contactState === 'running') {
                const proceed = confirm(
                    '⚠️ Contact process is currently running.\n\n' +
                    'Editing search parameters while contacting is active may affect the process.\n\n' +
                    'Do you want to enter edit mode anyway?'
                );
                if (!proceed) {
                    return; // User chose not to edit while running
                }
            }

            if (this.editMode) {
                // Exiting edit mode - update current search with form data
                if (this.currentSearch) {
                    console.log('Saving edit mode changes...');
                    console.log('Form title:', this.searchParams.title);
                    console.log('Current search name before update:', this.currentSearch.name);

                    // Update the current search with form values
                    this.currentSearch.name = this.searchParams.title.trim();
                    this.currentSearch.parameters = {
                        ...this.searchParams,
                        zipcode: this.customerInfo.zipcode
                    };

                    console.log('Current search name after update:', this.currentSearch.name);

                    // Save to the searches list
                    this.saveSearchToList();
                }
                this.saveState();
                console.log('💾 Edit mode ended - changes saved');
            } else {
                console.log('✏️ Edit mode started');
            }

            this.editMode = !this.editMode;
        },
        getDealershipCount(make) {
            return this.masterDealerships.filter(d => d.make === make).length;
        },

        // Distance Display Helper
        getDisplayDistance(parameters) {
            if (parameters.distance === 'other') {
                return parameters.customDistance || 'Custom';
            }
            return parameters.distance;
        },

        // Address and Maps Methods
        getFullAddress(dealer) {
            const parts = [];
            if (dealer.address_line1) parts.push(dealer.address_line1);
            if (dealer.city) parts.push(dealer.city);
            if (dealer.state) parts.push(dealer.state);

            // Fix zipcode - only show first 5 digits
            if (dealer.zip_code) {
                const cleanZip = dealer.zip_code.toString().substring(0, 5);
                parts.push(cleanZip);
            }

            return parts.join(', ') || 'Address not available';
        },

        getGoogleMapsUrl(dealer) {
            const userZip = this.customerInfo.zipcode || this.searchParams.zipcode || '';
            const dealerAddress = this.getFullAddress(dealer);

            // Create Google Maps directions URL
            const baseUrl = 'https://www.google.com/maps/dir/';
            const origin = encodeURIComponent(userZip);
            const destination = encodeURIComponent(dealerAddress);

            return `${baseUrl}${origin}/${destination}`;
        },

        // === PERSISTENT STORAGE API METHODS ===

        async saveSearchesToServer() {
            try {
                const response = await fetch('/api/searches', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ searches: this.savedSearches })
                });

                if (!response.ok) {
                    throw new Error(`Server responded with ${response.status}`);
                }

                const result = await response.json();
                if (result.success) {
                    console.log(`✅ Server save: ${result.message}`);
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                console.error('Failed to save searches to server:', error);
                throw error; // Re-throw to allow fallback handling
            }
        },

        async loadSearchesFromServer() {
            try {
                const response = await fetch('/api/searches');
                if (!response.ok) {
                    throw new Error(`Server responded with ${response.status}`);
                }

                const result = await response.json();
                if (result.success) {
                    this.savedSearches = result.searches || [];
                    console.log(`📖 Server load: Loaded ${this.savedSearches.length} searches`);
                    this.savedSearches.forEach(search => {
                        if (search && Array.isArray(search.dealerships)) {
                            this.applyContactOverridesToDealers(search.dealerships);
                        }
                    });
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                console.error('Failed to load searches from server:', error);
                throw error; // Re-throw to allow fallback handling
            }
        },

        async saveStateToServer() {
            try {
                const state = {
                    currentView: this.currentView,
                    currentSearch: this.currentSearch,
                    customerInfo: this.customerInfo,
                    searchParams: this.searchParams
                };

                const response = await fetch('/api/state', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ state })
                });

                if (!response.ok) {
                    throw new Error(`Server responded with ${response.status}`);
                }

                const result = await response.json();
                if (result.success) {
                    console.log(`✅ Server state save: ${result.message}`);
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                console.error('Failed to save state to server:', error);
                throw error;
            }
        },

        async loadStateFromServer() {
            try {
                const response = await fetch('/api/state');
                if (!response.ok) {
                    throw new Error(`Server responded with ${response.status}`);
                }

                const result = await response.json();
                if (result.success && result.state) {
                    const state = result.state;
                    this.currentView = state.currentView || 'search-list';
                    this.currentSearch = state.currentSearch;
                    this.customerInfo = state.customerInfo || {
                        firstName: 'Ilias',
                        lastName: 'Beshimov',
                        email: 'ilias.beshimov@gmail.com',
                        phone: '415-340-4828',
                        zipcode: '',
                        message: ''
                    };
                    this.searchParams = state.searchParams || { title: '', make: '', distance: '100', customDistance: '' };
                    console.log(`📖 Server state load: Loaded application state`);

                    if (this.currentSearch && Array.isArray(this.currentSearch.dealerships)) {
                        this.applyContactOverridesToDealers(this.currentSearch.dealerships);
                    }
                } else {
                    console.log('No state found on server, using defaults');
                }
            } catch (error) {
                console.error('Failed to load state from server:', error);
                throw error;
            }
        },

        async createServerBackup() {
            try {
                const response = await fetch('/api/backup', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });

                if (!response.ok) {
                    throw new Error(`Server responded with ${response.status}`);
                }

                const result = await response.json();
                if (result.success) {
                    console.log(`📦 Server backup: ${result.message}`);
                    alert(`Backup created: ${result.filename}`);
                } else {
                    throw new Error(result.error);
                }
            } catch (error) {
                console.error('Failed to create server backup:', error);
                alert('Failed to create server backup: ' + error.message);
            }
        }
    },

    computed: {
        websocketUrl() {
            // Computed property ensures methods are available when called
            // In production, use same host as page
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                return 'ws://localhost:8001/ws/contact';
            } else {
                // Production: use wss:// for secure connection
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                const host = window.location.host;
                return `${protocol}//${host}/ws/contact`;
            }
        },
        websocketStatusText() {
            const statusMap = {
                'disconnected': 'Disconnected from automation server',
                'connecting': 'Connecting to automation server...',
                'connected': 'Connected to automation server'
            };
            return statusMap[this.websocketStatus] || 'Unknown';
        },
        sortedSavedSearches() {
            // Sort searches by most recent update (createdAt or lastExpanded)
            return [...this.savedSearches].sort((a, b) => {
                const dateA = new Date(a.createdAt || a.lastExpanded || 0);
                const dateB = new Date(b.createdAt || b.lastExpanded || 0);
                return dateB - dateA; // Most recent first
            });
        },
        sortedDealerships() {
            if (!this.currentSearch) return [];
            return this.currentSearch.dealerships;
        },
        contactedCount() {
            if (!this.currentSearch) return 0;
            return this.currentSearch.dealerships.filter(d => d.contactStatus === 'contacted').length;
        },
        totalDealerships() {
            if (!this.currentSearch) return 0;
            return this.currentSearch.dealerships.length;
        },
        selectedCount() {
            if (!this.currentSearch) return 0;
            return this.currentSearch.dealerships.filter(d => d.selected).length;
        },
        hasSelectedDealerships() {
            return this.selectedCount > 0;
        },
        successCount() {
            if (!this.currentSearch) return 0;
            return this.currentSearch.dealerships.filter(d => d.contactStatus === 'contacted').length;
        },
        failedCount() {
            if (!this.currentSearch) return 0;
            return this.currentSearch.dealerships.filter(d => d.contactStatus === 'failed' || d.contactStatus === 'manual').length;
        },
        pendingCount() {
            if (!this.currentSearch) return 0;
            return this.currentSearch.dealerships.filter(d => d.contactStatus === 'pending').length;
        },
        successRate() {
            const attempted = this.successCount + this.failedCount;
            if (attempted === 0) return 0;
            return Math.round((this.successCount / attempted) * 100);
        },
        hasFailedContacts() {
            return this.failedCount > 0;
        },
        progressPercentage() {
            if (!this.currentSearch || this.selectedCount === 0) return 0;
            const completed = this.currentSearch.dealerships.filter(d =>
                d.selected && ['contacted', 'failed', 'manual'].includes(d.contactStatus)
            ).length;
            return Math.round((completed / this.selectedCount) * 100);
        },
        estimatedTimeRemaining() {
            if (this.contactState !== 'running' || this.selectedCount === 0) return 'N/A';
            const completed = this.currentSearch.dealerships.filter(d =>
                d.selected && ['contacted', 'failed', 'manual'].includes(d.contactStatus)
            ).length;
            const remaining = this.selectedCount - completed;
            if (remaining <= 0) return '0 minutes';

            // Estimate 2 seconds per dealer (as per current interval)
            const estimatedSeconds = remaining * 2;
            const minutes = Math.floor(estimatedSeconds / 60);
            const seconds = estimatedSeconds % 60;

            if (minutes > 0) {
                return `${minutes}m ${seconds}s`;
            } else {
                return `${seconds}s`;
            }
        }
    },

    async mounted() {
        console.log('[App] Mounting Vue application...');

        // Ensure modal is closed on mount
        this.showScreenshotModal = false;
        this.currentScreenshotUrl = null;
        this.currentScreenshotInfo = null;

        await this.loadInitialData();
        await this.loadState();

        // Initialize WebSocket connection
        if (typeof window.websocketMethods === 'object' && window.websocketMethods !== null) {
            try {
                // Merge WebSocket methods into this instance
                Object.keys(window.websocketMethods).forEach(key => {
                    if (typeof window.websocketMethods[key] === 'function') {
                        this[key] = window.websocketMethods[key].bind(this);
                    }
                });

                // Connect to WebSocket server
                if (typeof this.initializeWebSocket === 'function') {
                    this.initializeWebSocket();
                } else {
                    console.error('[App] initializeWebSocket method not found');
                }
            } catch (error) {
                console.error('[App] Error merging WebSocket methods:', error);
            }
        } else {
            console.warn('[App] WebSocket integration not loaded or invalid');
        }

        // Set up auto-save interval for persistent storage
        setInterval(async () => {
            await this.saveState();
        }, 30000); // Auto-save every 30 seconds

        window.addEventListener('beforeunload', this.saveState);

        console.log('[App] Vue application mounted successfully');
    },
    beforeUnmount() {
        window.removeEventListener('beforeunload', this.saveState);

        // Cleanup WebSocket connection
        if (this.websocketClient) {
            try {
                this.websocketClient.stopPingInterval();
                this.websocketClient.disconnect();
                console.log('[App] WebSocket client cleaned up on unmount');
            } catch (e) {
                console.error('[App] Error cleaning up WebSocket on unmount:', e);
            }
        }
    }
});

console.log('[App] Vue app created, attempting to mount...');
app.mount('#app');
console.log('[App] Vue app mounted successfully!');

} catch (error) {
    console.error('[App] FATAL ERROR:', error);
    console.error('[App] Stack:', error.stack);
    document.body.innerHTML = '<div style="padding: 20px; background: #fee; border: 2px solid #c33; margin: 20px; font-family: monospace;"><h1 style="color: #c33;">Vue Initialization Error</h1><p><strong>Error:</strong> ' + error.message + '</p><pre>' + error.stack + '</pre></div>';
}

// --- Classes from the specification ---

class CSVDataParser {
  parseCSV(csvText) {
    try {
      const lines = csvText.split('\n');
      if (lines.length < 2) {
        throw new Error('CSV file must have at least a header and one data row');
      }

      const headers = this.parseCSVLine(lines[0]).map(h => h.trim());
      console.log('CSV Headers found:', headers);

      if (!headers.includes('dealer_name') && !headers.includes('name')) {
        console.warn('No dealer_name or name column found. Available headers:', headers);
      }

      const dealers = lines.slice(1)
        .filter(line => line.trim()) // Skip empty lines
        .map((line, index) => {
          try {
            const values = this.parseCSVLine(line);
            const dealer = {};

            headers.forEach((header, i) => {
              dealer[header] = values[i] || '';
            });

            // Handle different possible column names
            const dealerName = dealer.dealer_name || dealer.name || dealer.Name || `Dealer ${index + 1}`;
            const make = dealer.Make || dealer.make || dealer.MAKE || 'Unknown';
            const latitude = parseFloat(dealer.latitude || dealer.lat) || 0;
            const longitude = parseFloat(dealer.longitude || dealer.lng || dealer.lon) || 0;

            return {
              ...dealer,
              id: `dealer_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, // More unique ID
              dealer_name: dealerName,
              make: make,
              latitude: latitude,
              longitude: longitude,
              contactStatus: 'pending',
              selected: true,
              lastContactedAt: null,
              contactSuccess: false,
              contactNotes: '',
              contactHistory: [],
              distanceMiles: 0
            };
          } catch (lineError) {
            console.error(`Error parsing line ${index + 1}:`, lineError);
            return null;
          }
        })
        .filter(dealer => dealer !== null); // Remove failed parses

      console.log(`Successfully parsed ${dealers.length} dealerships`);
      return dealers;

    } catch (error) {
      console.error('Error parsing CSV:', error);
      throw new Error(`CSV parsing failed: ${error.message}`);
    }
  }

  parseCSVLine(line) {
    const result = [];
    let current = '';
    let inQuotes = false;
    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      if (char === '"') {
        inQuotes = !inQuotes;
      } else if (char === ',' && !inQuotes) {
        result.push(current.trim());
        current = '';
      } else {
        current += char;
      }
    }
    result.push(current.trim());
    return result;
  }
}

class MakeManager {
  constructor(dealerships) {
    this.dealerships = dealerships || [];
    this.availableMakes = this.extractUniqueMakes();
  }

  extractUniqueMakes() {
    if (!this.dealerships || this.dealerships.length === 0) {
      console.warn('No dealerships provided to MakeManager');
      return [];
    }

    const makes = [...new Set(this.dealerships.map(d => d.make))]
      .filter(m => m && m.trim() !== '') // Filter out empty/null makes
      .sort();

    console.log(`Extracted ${makes.length} unique makes:`, makes);
    return makes;
  }

  getDealershipCountByMake(make) {
    return this.dealerships.filter(d => d.make === make).length;
  }
}
