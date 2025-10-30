# Google Sheets Column Remapping Instructions

**Date:** October 30, 2025
**Issue:** "Unknown" appearing in Vehicle Make dropdown
**Cause:** `make` column exists in Google Sheet but not included in CSV export

---

## Problem

The Google Sheets CSV export endpoint only exports the **first 7 visible columns**:
```
state, dealerName, address, phone, websiteLink, inventoryLink, serviceLink
```

Your sheet contains additional columns (`make`, `lat`, `long`, `contactPageLink`), but they're positioned **after column G**, so they don't get exported.

---

## Solution: Reorder Columns in Google Sheets

### Step 1: Open the Google Sheet
Open: https://docs.google.com/spreadsheets/d/1rvZN95GJgmf3Jiv5LWUYJETPE42P1iZE88UTLV_J94k/edit

### Step 2: Select the "Master Production List" tab
Click on the tab at the bottom of the sheet.

### Step 3: Reorder Columns

**Option A: Move `make` to Column A (Recommended)**

1. Click on the column header for `make` column
2. Drag it to position A (leftmost)
3. New order: `make, state, dealerName, address, phone, websiteLink, inventoryLink, serviceLink`

**Option B: Move important columns within first 7 positions**

Recommended column order for CSV export:
```
A: make
B: state
C: dealerName
D: address
E: phone
F: websiteLink
G: contactPageLink
H: lat
I: long
J: inventoryLink
K: serviceLink
```

This ensures `make`, `contactPageLink`, `lat`, and `long` are all included in the CSV export.

### Step 4: Verify the Change

Run this command to check if `make` is now in the CSV:
```bash
curl -sL "https://docs.google.com/spreadsheets/d/1rvZN95GJgmf3Jiv5LWUYJETPE42P1iZE88UTLV_J94k/export?format=csv&gid=0" | head -1
```

**Expected output:**
```
make,state,dealerName,address,phone,websiteLink,contactPageLink
```

### Step 5: Refresh the Frontend

1. Open the frontend in your browser
2. Hard refresh: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)
3. Check the Vehicle Make dropdown - should show "Mercedes-Benz (386 dealers)"

---

## Alternative: No Changes Needed (Temporary Fix Applied)

If you don't want to reorder columns, the frontend now has a **temporary fix**:

```javascript
// app.js:156
make: (dealer.make && dealer.make !== 'Unknown') ? dealer.make : 'Mercedes-Benz'
```

This automatically converts 'Unknown' to 'Mercedes-Benz' during normalization.

**Limitations:**
- Only works for single-make datasets
- If you add Toyota, Honda, etc., you'll need to reorder columns

---

## Why CSV Export Only Includes 7 Columns

Google Sheets CSV export behavior:
- Exports all columns if sheet is small
- May limit export to visible/first N columns for large sheets
- No official documentation on exact cutoff
- Solution: Keep important columns in leftmost positions

---

## Future: Support Multiple Makes

Once columns are reordered and `make` is included in CSV:

1. **Add different makes to Google Sheet**
   - Mercedes-Benz dealers: `make = "Mercedes-Benz"`
   - Toyota dealers: `make = "Toyota"`
   - BMW dealers: `make = "BMW"`

2. **Frontend will automatically extract unique makes**
   - MakeManager reads all unique values from `make` column
   - Dropdown will show: "Mercedes-Benz (386)", "Toyota (120)", etc.

3. **User can filter by make**
   - Select make from dropdown
   - Only dealers of that make will be shown

---

## Verification Steps

### 1. Check Current CSV Export
```bash
curl -sL "https://docs.google.com/spreadsheets/d/1rvZN95GJgmf3Jiv5LWUYJETPE42P1iZE88UTLV_J94k/export?format=csv&gid=0" | head -3
```

### 2. Check Browser Console
Open browser console (F12) and look for:
```
Sample raw data (first dealership): { state: "Alabama", dealerName: "...", make: undefined }
Sample normalized data (first dealership): { make: "Mercedes-Benz", ... }
```

### 3. Check MakeManager Output
Console should show:
```
Extracted 1 unique makes: ["Mercedes-Benz"]
Available makes: Mercedes-Benz
```

---

## Summary

**Quick Fix (Already Applied):** Frontend defaults 'Unknown' to 'Mercedes-Benz'

**Proper Fix (Recommended):** Reorder Google Sheets columns to include `make` in first 7 columns

**Future Enhancement:** Add `contactPageLink`, `lat`, `long` to first 7 columns as well

---

**Document Version:** 1.0
**Last Updated:** October 30, 2025
**Status:** Temporary fix applied, column reordering recommended
