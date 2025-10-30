# Google Sheets Integration - Dealership Data Source

**Date:** October 30, 2025
**Version:** 1.0.1
**Status:** Production - Google Sheets as Primary Data Source

---

## Overview

The frontend now loads dealership data from **Google Sheets** as the primary source, with automatic fallback to local CSV files if unavailable. This provides a centralized, always-up-to-date data source that can be edited directly in Google Sheets.

---

## Data Source

**Google Sheet:** "Dealerships Unified Production"
**Sheet ID:** `1rvZN95GJgmf3Jiv5LWUYJETPE42P1iZE88UTLV_J94k`
**Tab:** "Master Production List" (gid=0)
**URL:** https://docs.google.com/spreadsheets/d/1rvZN95GJgmf3Jiv5LWUYJETPE42P1iZE88UTLV_J94k/edit

**Export URL:**
```
https://docs.google.com/spreadsheets/d/1rvZN95GJgmf3Jiv5LWUYJETPE42P1iZE88UTLV_J94k/export?format=csv&gid=0
```

---

## Current Data

**Make:** Mercedes-Benz
**Total Dealerships:** 386
**Coverage:** All 50 US states + Puerto Rico

---

## Google Sheets Structure

### Current Columns (CSV Export):
```csv
state,dealerName,address,phone,websiteLink,inventoryLink,serviceLink
```

**Note:** The Google Sheet contains additional columns (like `make`, `lat`, `long`, `contactPageLink`) that are NOT currently exported in the CSV. The CSV export only includes the first 7 visible columns.

### Column Descriptions:

| Column | Description | Example |
|--------|-------------|---------|
| `state` | US State | "Alabama", "California" |
| `dealerName` | Dealership name | "Mercedes-Benz of Mobile" |
| `address` | Full address | "3060 Dauphin Street Mobile, AL, 36606" |
| `phone` | Phone number | "(251) 472-2369" |
| `websiteLink` | Dealership website | "mbofmobile.com" |
| `inventoryLink` | Inventory page URL | "https://www.mbusa.com/en/inventory/..." |
| `serviceLink` | Service page URL | "http://www.mbofmobile.com/service/..." |

### Columns to Add to CSV Export:

**Current Issue:** The Google Sheet has these columns, but they're not included in the CSV export:

| Column | Purpose | Status | Populated By |
|--------|---------|--------|--------------|
| `make` | Vehicle make | Exists in sheet, NOT in CSV export | Manual (default: "Mercedes-Benz") |
| `contactPageLink` | Contact form URL | Exists in sheet, NOT in CSV export | Automation (when detected) |
| `lat` | Latitude | Exists in sheet, NOT in CSV export | Geocoding script |
| `long` | Longitude | Exists in sheet, NOT in CSV export | Geocoding script |

**Solution:** Reorder columns in Google Sheets so that `make`, `lat`, `long`, and `contactPageLink` are in the first 7 columns (columns A-G), OR move them before the export cutoff point.

**Temporary Fix Applied:** The frontend now defaults to 'Mercedes-Benz' when `make` column is missing or set to 'Unknown' (see `app.js:156`).

---

## Frontend Integration

### Loading Process

**File:** `frontend/app.js`
**Method:** `loadInitialData()` (line 63)

**Load Order:**
1. **Google Sheets (Primary)** - Always tries first
2. **Local CSV (Backup)** - `./Dealerships.csv`
3. **Root CSV (Backup)** - `../Dealerships.csv`

```javascript
const sources = [
    { url: GOOGLE_SHEETS_URL, name: 'Google Sheets (Production)', isGoogleSheets: true },
    { url: './Dealerships.csv', name: 'Local CSV (Backup)', isGoogleSheets: false },
    { url: '../Dealerships.csv', name: 'Root CSV (Backup)', isGoogleSheets: false }
];
```

### Data Normalization

Google Sheets data is automatically normalized to match the expected format:

**Input (Google Sheets):**
```javascript
{
    state: "Alabama",
    dealerName: "Mercedes-Benz of Mobile",
    address: "3060 Dauphin Street Mobile, AL, 36606",
    phone: "(251) 472-2369",
    websiteLink: "mbofmobile.com",
    inventoryLink: "https://...",
    serviceLink: "http://..."
}
```

**Output (Normalized):**
```javascript
{
    make: "Mercedes-Benz",
    dealer_name: "Mercedes-Benz of Mobile",
    state: "Alabama",
    city: "Mobile",
    zip_code: "36606",
    address_line1: "3060 Dauphin Street",
    full_address: "3060 Dauphin Street Mobile, AL, 36606",
    phone: "(251) 472-2369",
    website: "mbofmobile.com",
    inventory_link: "https://...",
    service_link: "http://...",
    contact_page_link: "",  // To be populated
    latitude: null,  // To be populated
    longitude: null,  // To be populated
    data_source: "google_sheets"
}
```

### Address Parsing

**Method:** `parseAddress(addressString)` (line 190)

**Input Format:** `"Street Address City, ST, ZIP"`

**Examples:**
```
"3060 Dauphin Street Mobile, AL, 36606"
  → street: "3060 Dauphin Street"
  → city: "Mobile"
  → state: "AL"
  → zip: "36606"

"217 Eastern Blvd. Montgomery, AL, 36124"
  → street: "217 Eastern Blvd."
  → city: "Montgomery"
  → state: "AL"
  → zip: "36124"
```

**Regex Pattern:**
```javascript
/^(.+?)\s+([A-Za-z\s]+),\s*([A-Z]{2}),?\s*(\d{5}(?:-\d{4})?)$/
```

---

## Benefits

### ✅ Centralized Data Management
- Single source of truth in Google Sheets
- No need to update multiple CSV files
- Edit directly in spreadsheet interface

### ✅ Always Up-to-Date
- Frontend fetches latest data on every page load
- No manual file synchronization required
- Changes immediately available

### ✅ Automatic Fallback
- If Google Sheets unavailable, uses local CSV backup
- Graceful degradation ensures app always works
- No single point of failure

### ✅ Easy Collaboration
- Multiple people can update Google Sheet
- Version history and change tracking
- Comments and notes in spreadsheet

### ✅ Data Enrichment Ready
- Can add `contactPageLink` as automation discovers it
- Can add `lat`/`long` as geocoding completes
- Spreadsheet grows with automation progress

---

## Validation

### Minimal Requirements (Google Sheets Source):
- ✅ `dealer_name` - Must be present
- ✅ `website` - Must be present

**Relaxed validation** because:
- `latitude`/`longitude` will be populated over time
- `zip_code` extracted from address field
- Missing fields don't break core functionality

### Standard Requirements (Local CSV):
- ✅ `dealer_name`
- ✅ `website`
- ✅ `latitude`
- ✅ `longitude`
- ✅ `zip_code`

---

## Updating the Data

### To Add Dealerships:
1. Open Google Sheet
2. Add row with: `state, dealerName, address, phone, websiteLink, inventoryLink, serviceLink`
3. Save (auto-saves)
4. Frontend automatically loads on next page refresh

### To Update Dealership Info:
1. Open Google Sheet
2. Edit cells directly
3. Save
4. Frontend reflects changes immediately

### To Add Contact Page URLs:
**Option A: Manual Entry**
1. Run contact page automation
2. Note discovered URL
3. Add to `contactPageLink` column (if added to sheet)

**Option B: Automation (Future)**
- Backend service discovers contact pages
- Writes back to Google Sheets via API
- Requires Google Sheets API setup

---

## CORS and Permissions

### Google Sheets Export Requirements:

**Share Settings:**
- ✅ Link sharing: "Anyone with the link"
- ✅ Permission: "Viewer"
- ✅ Public access: Required for CSV export

**Why Public?**
- CSV export endpoint requires public access
- No authentication header in browser fetch
- Data is not sensitive (public dealership info)

**Alternative (More Secure):**
- Use Google Sheets API with API key
- Backend proxy with server-side credentials
- Requires additional setup

---

## Future Enhancements

### Phase 1: Add Missing Columns
1. **Add `make` column** - Manual entry (default: "Mercedes-Benz")
2. **Add `contactPageLink` column** - Populated by automation
3. **Add `lat` column** - Populated by geocoding
4. **Add `long` column** - Populated by geocoding

### Phase 2: Geocoding Integration
**Script to populate `lat`/`long`:**
```javascript
// Pseudocode
for each dealership:
    if (!dealership.lat || !dealership.long):
        address = dealership.address
        coords = geocode(address)  // Google Maps API
        update_sheet(row, coords.lat, coords.long)
```

### Phase 3: Contact Page Discovery Write-Back
**Automation writes discovered URLs:**
```javascript
// After contact page found
if (contactPageUrl):
    update_google_sheet(dealership.name, {
        contactPageLink: contactPageUrl
    })
```

**Requires:**
- Google Sheets API credentials
- OAuth or Service Account
- Backend endpoint for writes

### Phase 4: Multi-Make Support
**Add more brands:**
1. Create new tabs for other makes (Toyota, Honda, etc.)
2. Update frontend to load multiple tabs
3. Merge data from all tabs
4. Filter by make in UI

---

## Troubleshooting

### Issue: "Failed to load Google Sheets"

**Possible Causes:**
1. Sheet is not public
2. Network error / no internet
3. Google Sheets service down
4. CORS policy blocking request

**Solution:**
- Check share settings (must be "Anyone with link")
- Verify network connectivity
- Check browser console for errors
- Falls back to local CSV automatically

### Issue: "Dealerships have missing fields"

**Cause:** Address parsing failed

**Solution:**
- Check address format matches expected pattern
- Update `parseAddress()` regex if needed
- Add manual overrides for non-standard addresses

### Issue: "Unknown" in Vehicle Make dropdown

**Cause:** `make` column exists in Google Sheet but not included in CSV export

**Root Cause:**
1. Google Sheets CSV export only includes first 7 visible columns
2. `make` column is positioned after column G (serviceLink)
3. CSV parser sets missing makes to 'Unknown'

**Solution Options:**

**Option A: Reorder Google Sheets columns (Recommended)**
1. Open Google Sheet
2. Move `make` column to position A (before `state`)
3. Reorder as: `make, state, dealerName, address, phone, websiteLink, inventoryLink`
4. CSV export will now include make

**Option B: Use existing default (Already Applied)**
- Frontend now automatically converts 'Unknown' to 'Mercedes-Benz'
- No Google Sheet changes needed
- Works for single-make datasets

**Verification:**
```bash
# Check if make column is in CSV export
curl -sL "https://docs.google.com/spreadsheets/d/1rvZN95GJgmf3Jiv5LWUYJETPE42P1iZE88UTLV_J94k/export?format=csv&gid=0" | head -1
```

### Issue: "No makes available"

**Cause:** All dealerships filtered out or `make` field is null

**Solution:**
- Check browser console for validation errors
- Verify `make` field is being set in normalization
- Defaults to "Mercedes-Benz" if not present

---

## Code References

**Frontend Integration:**
- `frontend/app.js:63-138` - `loadInitialData()` method
- `frontend/app.js:140-188` - `normalizeGoogleSheetsData()` method
- `frontend/app.js:190-226` - `parseAddress()` method

**Google Sheets URL:**
- CSV Export: Line 66 in `frontend/app.js`
- Sheet ID: `1rvZN95GJgmf3Jiv5LWUYJETPE42P1iZE88UTLV_J94k`

---

## Testing

### Manual Test Procedure:

1. **Open frontend in browser**
   ```bash
   cd frontend
   python3 -m http.server 8000
   # Open http://localhost:8000
   ```

2. **Check browser console**
   - Should see: `"Attempting to load from: Google Sheets (Production)"`
   - Should see: `"✅ Successfully loaded 386 dealerships from Google Sheets (Production)"`
   - Should see: `"Available makes: Mercedes-Benz"`

3. **Verify data loaded**
   - UI should show dealerships
   - Filter by state should work
   - Search should work

4. **Test fallback**
   - Disconnect internet
   - Refresh page
   - Should load from local CSV backup

### Automated Testing:

```javascript
// Test address parsing
console.assert(
    parseAddress("3060 Dauphin Street Mobile, AL, 36606").zip === "36606",
    "Zip code parsing failed"
);

// Test normalization
const normalized = normalizeGoogleSheetsData({
    state: "AL",
    dealerName: "Test Dealer",
    address: "123 Main St City, AL, 12345",
    phone: "555-1234",
    websiteLink: "example.com"
});
console.assert(normalized.dealer_name === "Test Dealer", "Name normalization failed");
console.assert(normalized.zip_code === "12345", "Zip extraction failed");
```

---

## Security Considerations

### Data Privacy:
- ✅ Dealership data is public information (addresses, phones, websites)
- ✅ No sensitive customer data in sheet
- ✅ Read-only access from frontend

### API Rate Limits:
- Google Sheets export has no published rate limit for public sheets
- Caching in browser (no aggressive refresh)
- Falls back to local CSV if unavailable

### Write Access:
- Currently read-only from frontend
- Future write-back requires authentication
- Use service account for backend writes

---

## Summary

**Before:**
- ❌ Static CSV files in repository
- ❌ Manual file updates and sync
- ❌ No easy way to track changes
- ❌ Single file location

**After:**
- ✅ Google Sheets as primary source
- ✅ Automatic data updates
- ✅ Version history and collaboration
- ✅ Automatic fallback to local CSV
- ✅ Data normalization and parsing
- ✅ Ready for geocoding and contact discovery write-back

**Next Steps:**
1. Add `make`, `contactPageLink`, `lat`, `long` columns to Google Sheet
2. Implement geocoding script to populate coordinates
3. Set up Google Sheets API for write-back
4. Add contact page discovery automation

---

**Document Version:** 1.0
**Last Updated:** October 30, 2025
**Owner:** Development Team
