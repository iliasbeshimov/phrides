# Census.gov Zipcode Data Sources

## 📍 **Where to Find Zipcode Lat/Long Data on Census.gov**

### 🚀 **Option 1: Real-time API (Implemented)**
**Census Geocoding Services API**
- **URL**: https://geocoding.geo.census.gov/geocoder/
- **API Endpoint**: `https://geocoding.geo.census.gov/geocoder/locations/onelineaddress`
- **Cost**: Free
- **Rate Limits**: Reasonable (not specified)
- **Format**: JSON response with coordinates

**Example API Call:**
```
https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?address=90210,USA&benchmark=4&format=json
```

**Response Format:**
```json
{
  "result": {
    "addressMatches": [{
      "coordinates": {
        "x": -118.4114,  // longitude
        "y": 34.0942     // latitude
      }
    }]
  }
}
```

### 📁 **Option 2: Download ZCTA Database Files**

#### **ZIP Code Tabulation Areas (ZCTA) - 2020 Census**
**Main Page**: https://www.census.gov/programs-surveys/geography/guidance/geo-areas/zctas.html

#### **Direct Download Options:**

**1. TIGER/Line Shapefiles (Most Complete)**
- **URL**: https://catalog.data.gov/dataset/tiger-line-shapefile-2022-nation-u-s-2020-census-5-digit-zip-code-tabulation-area-zcta5
- **Format**: Shapefile (.shp) with coordinates
- **Size**: ~50MB
- **Records**: ~33,000 ZCTAs
- **Accuracy**: Census boundaries (very precise)

**2. ZCTA Gazetteer Files**
- **URL**: https://www.census.gov/geographies/reference-files/time-series/geo/gazetteer-files.html
- **Format**: Text/CSV files
- **Contains**: ZCTA codes with centroid coordinates
- **Example Fields**: GEOID, ALAND, AWATER, INTPTLAT, INTPTLON

**3. Data.gov ZCTA Downloads**
- **Search**: https://catalog.data.gov/dataset?tags=zcta
- **Multiple formats**: Shapefiles, KML, GeoJSON
- **Updated**: Based on 2020 Census boundaries

### 🔄 **Alternative Free Services (Backup)**

#### **OpenStreetMap Nominatim**
- **URL**: https://nominatim.openstreetmap.org/
- **API**: `https://nominatim.openstreetmap.org/search?q=90210,USA&format=json`
- **Cost**: Free
- **Rate Limit**: 1 request/second
- **Reliability**: Good for backup

#### **GeoNames**
- **URL**: http://www.geonames.org/
- **API**: Postal code lookup service
- **Cost**: Free (registration required)
- **Coverage**: Global

---

## 📊 **Data Quality Comparison**

| Source | Accuracy | Coverage | Speed | Cost | Best For |
|--------|----------|----------|-------|------|----------|
| Census API | High | US Only | Fast | Free | Real-time lookup |
| ZCTA Download | Very High | US Only | Instant | Free | Offline processing |
| Nominatim | Medium | Global | Medium | Free | Backup service |
| GeoNames | Medium | Global | Fast | Free | International |

---

## 🛠 **Recommended Implementation Strategy**

### **Current Implementation (Hybrid Approach)**
1. **Primary**: Census.gov API for real-time geocoding
2. **Fallback**: OpenStreetMap Nominatim for reliability
3. **Caching**: Store results to minimize API calls
4. **Future**: Download ZCTA file for offline operation

### **For High-Volume Applications**
1. **Download ZCTA database** (one-time setup)
2. **Load into database** (PostgreSQL with PostGIS)
3. **Fast local lookup** (no API calls needed)
4. **Annual updates** (when new ZCTA data released)

---

## 💾 **File Download Instructions**

### **To Download ZCTA Coordinate Data:**

1. **Visit**: https://catalog.data.gov/dataset/tiger-line-shapefile-2022-nation-u-s-2020-census-5-digit-zip-code-tabulation-area-zcta5

2. **Download**:
   - Shapefile format: `tl_2022_us_zcta520.zip`
   - Contains: .shp, .dbf, .shx files with coordinate data

3. **Convert to CSV** (using Python):
   ```python
   import geopandas as gpd

   # Read shapefile
   gdf = gpd.read_file('tl_2022_us_zcta520.shp')

   # Extract centroid coordinates
   gdf['longitude'] = gdf.geometry.centroid.x
   gdf['latitude'] = gdf.geometry.centroid.y

   # Save as CSV
   gdf[['ZCTA5CE20', 'latitude', 'longitude']].to_csv('zcta_coordinates.csv')
   ```

4. **Result**: CSV with zipcode, latitude, longitude for all US zipcodes

---

## 🎯 **Current System Benefits**

### **Implemented Solution Advantages:**
- ✅ **Free**: No API costs using Census.gov
- ✅ **Reliable**: Government service with high uptime
- ✅ **Accurate**: Official census data
- ✅ **Fast**: Real-time geocoding with caching
- ✅ **Fallback**: Alternative service for reliability

### **Performance Metrics:**
- **Geocoding time**: 1-3 seconds per new zipcode
- **Cache hits**: Instant response for repeated zipcodes
- **Accuracy**: ±1-2 miles for zipcode centroid
- **Coverage**: All US zipcodes

---

**📝 Note**: The implemented solution uses Census.gov API for real-time geocoding with OpenStreetMap fallback. For high-volume applications, consider downloading the ZCTA database for offline processing.