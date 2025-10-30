#!/usr/bin/env node

/**
 * Simple Express server with persistent JSON storage for dealership contact manager
 * Provides REST API endpoints to save/load searches and maintains data across restarts
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8080;

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.static(__dirname)); // Serve static files from current directory

// Data storage paths
const DATA_DIR = path.join(__dirname, 'data');
const SEARCHES_FILE = path.join(DATA_DIR, 'saved_searches.json');
const STATE_FILE = path.join(DATA_DIR, 'app_state.json');

// Ensure data directory exists
if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    console.log(`📁 Created data directory: ${DATA_DIR}`);
}

// Helper functions
function readJsonFile(filePath, defaultValue = null) {
    try {
        if (fs.existsSync(filePath)) {
            const data = fs.readFileSync(filePath, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error(`Error reading ${filePath}:`, error);
    }
    return defaultValue;
}

function writeJsonFile(filePath, data) {
    try {
        fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf8');
        return true;
    } catch (error) {
        console.error(`Error writing ${filePath}:`, error);
        return false;
    }
}

// API Routes

// Get all saved searches
app.get('/api/searches', (req, res) => {
    const searches = readJsonFile(SEARCHES_FILE, []);
    console.log(`📖 Loaded ${searches.length} searches`);
    res.json({ success: true, searches });
});

// Save all searches
app.post('/api/searches', (req, res) => {
    const { searches } = req.body;

    if (!Array.isArray(searches)) {
        return res.status(400).json({
            success: false,
            error: 'Invalid data format: searches must be an array'
        });
    }

    const success = writeJsonFile(SEARCHES_FILE, searches);

    if (success) {
        console.log(`💾 Saved ${searches.length} searches to disk`);
        res.json({ success: true, message: `Saved ${searches.length} searches` });
    } else {
        res.status(500).json({ success: false, error: 'Failed to save searches' });
    }
});

// Get application state
app.get('/api/state', (req, res) => {
    const state = readJsonFile(STATE_FILE, {});
    console.log(`📖 Loaded application state`);
    res.json({ success: true, state });
});

// Save application state
app.post('/api/state', (req, res) => {
    const { state } = req.body;

    if (!state || typeof state !== 'object') {
        return res.status(400).json({
            success: false,
            error: 'Invalid data format: state must be an object'
        });
    }

    // Add timestamp to state
    state.lastSaved = new Date().toISOString();

    const success = writeJsonFile(STATE_FILE, state);

    if (success) {
        console.log(`💾 Saved application state to disk`);
        res.json({ success: true, message: 'Application state saved' });
    } else {
        res.status(500).json({ success: false, error: 'Failed to save state' });
    }
});

// Backup endpoint - create timestamped backup
app.post('/api/backup', (req, res) => {
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const backupDir = path.join(DATA_DIR, 'backups');

    if (!fs.existsSync(backupDir)) {
        fs.mkdirSync(backupDir, { recursive: true });
    }

    try {
        const searches = readJsonFile(SEARCHES_FILE, []);
        const state = readJsonFile(STATE_FILE, {});

        const backupData = {
            timestamp,
            searches,
            state,
            version: '1.0'
        };

        const backupFile = path.join(backupDir, `backup-${timestamp}.json`);
        const success = writeJsonFile(backupFile, backupData);

        if (success) {
            console.log(`📦 Created backup: ${backupFile}`);
            res.json({
                success: true,
                message: 'Backup created successfully',
                filename: `backup-${timestamp}.json`
            });
        } else {
            res.status(500).json({ success: false, error: 'Failed to create backup' });
        }
    } catch (error) {
        console.error('Backup creation failed:', error);
        res.status(500).json({ success: false, error: 'Backup creation failed' });
    }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
    const searches = readJsonFile(SEARCHES_FILE, []);
    const state = readJsonFile(STATE_FILE, {});

    res.json({
        success: true,
        status: 'healthy',
        data: {
            searchesCount: searches.length,
            hasState: Object.keys(state).length > 0,
            dataDirectory: DATA_DIR
        }
    });
});

// Serve the main application
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log('🚀 Dealership Contact Manager Server');
    console.log('=' * 50);
    console.log(`📍 Server running at: http://localhost:${PORT}`);
    console.log(`📁 Data directory: ${DATA_DIR}`);
    console.log(`📊 API endpoints:`);
    console.log(`   GET  /api/searches - Load saved searches`);
    console.log(`   POST /api/searches - Save searches`);
    console.log(`   GET  /api/state    - Load app state`);
    console.log(`   POST /api/state    - Save app state`);
    console.log(`   POST /api/backup   - Create backup`);
    console.log(`   GET  /api/health   - Health check`);

    // Show current data status
    const searches = readJsonFile(SEARCHES_FILE, []);
    const state = readJsonFile(STATE_FILE, {});
    console.log(`💾 Current data: ${searches.length} searches, state: ${Object.keys(state).length > 0 ? 'loaded' : 'empty'}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Shutting down server gracefully...');
    process.exit(0);
});