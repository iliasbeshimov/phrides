# Project Workflow & Development Log

This document outlines the development process and key architectural decisions made during the creation of the Local Dealership Contact Management System.

## 1. Initial Goal

The initial request was to design and implement a browser-based UI for an existing automotive dealership contact automation system. The core requirements were to allow a user to define a search (make, location), find dealerships, and manage an automated contact process.

## 2. Security Interruption: API Key Removal

Shortly after starting, a critical security alert was raised regarding exposed API keys in the project's git history. Development was paused to address this immediately.

- **Identification:** Multiple Google Maps and Mapbox API keys were found in HTML test fixtures.
- **Action:**
    1.  All identified keys were scrubbed from the files and replaced with a `REMOVED_FOR_SECURITY` placeholder.
    2.  The `.gitignore` file was significantly enhanced with patterns to prevent future accidental commits of `.env` files, API keys, and other secrets.
    3.  A `pre-commit` git hook was implemented to scan staged files for API key patterns and block the commit if any are found.
- **Resolution:** The repository was secured, and guidance was provided on revoking the exposed keys.

## 3. Specification Refinement

With the security issue resolved, we returned to the application design. The initial specifications were critically analyzed to simplify development and increase robustness. This led to several key pivots:

- **From Server-Based to Local-First:** The architecture was changed from a Python backend (FastAPI) and React frontend to a **100% local, browser-based application** using vanilla JavaScript (with Vue.js for reactivity) and CSS. This eliminated the need for a server, database, and user authentication for the MVP.
- **From External APIs to Local Data:** The dependency on live geocoding APIs was identified as a blocker for an offline-first app.
    - **Action:** We located a downloadable zip code database from the US Census Bureau (ZCTA Gazetteer File).
    - **Implementation:** A Python script (`scripts/process_zip_data.py`) was created to process this large text file into an efficient `zip_coordinates.js` file, which acts as a local database.
- **From Complex to Simple Search:** The logic for handling search parameter changes was simplified. Instead of automatically detecting changes, we moved to an explicit "Update Search" button. The behavior was defined as purely additive to prevent accidental data loss.
- **UI Unification:** Based on user feedback, the "Search Parameters" and "Customer Information" UI panels were merged into a single "Search & Contact Details" panel with a single, shared zip code field.

## 4. Final Implemented Architecture

The final application lives in the `frontend/` directory and consists of:

- **`index.html`**: The main application view, structured with semantic HTML.
- **`style.css`**: The stylesheet for the application's layout and appearance.
- **`zip_coordinates.js`**: An auto-generated local database mapping ~34,000 US zip codes to their latitude/longitude.
- **`app.js`**: The core application logic, built with Vue.js 3. It handles:
    - **Data Loading:** Fetches and parses `Dealerships.csv` and the local zip code database.
    - **State Management:** Manages all UI and data state.
    - **Persistence:** Automatically saves and loads the application state (current search, contact progress) to the browser's `localStorage`.
    - **Search Logic:** Implements distance calculation (Haversine formula) and filtering.
    - **Contact Simulation:** Contains a simulated loop to demonstrate the auto-contacting process.

This iterative process of design, security hardening, simplification, and implementation resulted in a robust, offline-capable application that meets the user's core requirements.
