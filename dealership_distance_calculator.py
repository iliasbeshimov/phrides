#!/usr/bin/env python3
"""
DEALERSHIP DISTANCE CALCULATOR
Finds dealerships within specified distance using precise coordinates

Features:
- Census.gov API for zipcode geocoding (real-time)
- Haversine distance calculation for accuracy
- Make filtering (Jeep, Ram, Chrysler, etc.)
- Results sorted by distance
"""

import pandas as pd
import requests
import json
import math
from typing import List, Dict, Tuple, Optional
import time

class DealershipDistanceCalculator:
    def __init__(self, dealership_csv_path: str = "Dealerships - Jeep.csv"):
        """Initialize with dealership database"""
        self.dealership_csv_path = dealership_csv_path
        self.df = None
        self.zipcode_cache = {}  # Cache geocoded zipcodes
        self.load_dealership_data()

    def load_dealership_data(self):
        """Load dealership database"""
        try:
            self.df = pd.read_csv(self.dealership_csv_path)
            print(f"✅ Loaded {len(self.df)} dealerships from database")

            # Validate required columns
            required_cols = ['dealer_name', 'latitude', 'longitude', 'address_line1', 'city', 'state', 'zip_code']
            missing_cols = [col for col in required_cols if col not in self.df.columns]
            if missing_cols:
                print(f"⚠️ Warning: Missing columns: {missing_cols}")

        except Exception as e:
            print(f"❌ Error loading dealership data: {e}")
            raise

    def geocode_zipcode(self, zipcode: str) -> Optional[Tuple[float, float]]:
        """
        Geocode zipcode using Census.gov API and fallback methods
        Returns (latitude, longitude) or None if not found
        """
        # Check cache first
        if zipcode in self.zipcode_cache:
            return self.zipcode_cache[zipcode]

        # Clean zipcode (remove spaces, hyphens)
        clean_zipcode = zipcode.replace('-', '').replace(' ', '').strip()

        # Try multiple approaches
        coords = None

        # Method 1: Census API with zipcode + generic city/state
        coords = self._try_census_geocoding(clean_zipcode)

        # Method 2: Alternative free geocoding service
        if not coords:
            coords = self._try_alternative_geocoding(clean_zipcode)

        # Cache result (even if None)
        self.zipcode_cache[zipcode] = coords

        if coords:
            print(f"   ✅ Found: {coords[0]:.4f}, {coords[1]:.4f}")
        else:
            print(f"   ❌ No coordinates found for zipcode: {zipcode}")

        return coords

    def _try_census_geocoding(self, zipcode: str) -> Optional[Tuple[float, float]]:
        """Try Census.gov API with different address formats"""
        print(f"🔍 Geocoding zipcode: {zipcode} (Census API)")

        # Try different address formats
        address_formats = [
            f"{zipcode}, USA",  # Just zipcode
            f"Main St, {zipcode}",  # Generic street + zipcode
            f"1 Main Street, {zipcode}",  # Full generic address
        ]

        url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress"

        for address_format in address_formats:
            try:
                params = {
                    'address': address_format,
                    'benchmark': '4',
                    'format': 'json'
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()

                if (data.get('result', {}).get('addressMatches') and
                    len(data['result']['addressMatches']) > 0):

                    match = data['result']['addressMatches'][0]
                    coords = match.get('coordinates', {})

                    if 'x' in coords and 'y' in coords:
                        longitude = float(coords['x'])
                        latitude = float(coords['y'])
                        return (latitude, longitude)

            except Exception as e:
                continue

        return None

    def _try_alternative_geocoding(self, zipcode: str) -> Optional[Tuple[float, float]]:
        """Try alternative free geocoding service (OpenStreetMap Nominatim)"""
        print(f"🔍 Geocoding zipcode: {zipcode} (Alternative API)")

        try:
            # OpenStreetMap Nominatim (free, rate-limited)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': f"{zipcode}, USA",
                'format': 'json',
                'countrycodes': 'us',
                'limit': 1
            }

            headers = {
                'User-Agent': 'DealershipDistanceCalculator/1.0'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                result = data[0]
                latitude = float(result['lat'])
                longitude = float(result['lon'])
                return (latitude, longitude)

        except Exception as e:
            pass

        return None

    def haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate the great circle distance between two points on Earth
        Returns distance in miles
        """
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))

        # Radius of Earth in miles
        earth_radius_miles = 3959

        return c * earth_radius_miles

    def find_nearby_dealerships(self,
                              make: str,
                              zipcode: str,
                              radius_miles: float,
                              max_results: int = 50) -> List[Dict]:
        """
        Find dealerships within specified distance

        Args:
            make: Vehicle make (e.g., 'Jeep', 'Ram', 'Chrysler')
            zipcode: User zipcode (e.g., '90210')
            radius_miles: Search radius in miles
            max_results: Maximum number of results to return

        Returns:
            List of dealerships with distance information
        """
        print(f"🎯 Finding {make} dealerships within {radius_miles} miles of {zipcode}")

        # 1. Geocode user zipcode
        user_coords = self.geocode_zipcode(zipcode)
        if not user_coords:
            print(f"❌ Could not geocode zipcode: {zipcode}")
            return []

        user_lat, user_lng = user_coords
        print(f"📍 User location: {user_lat:.4f}, {user_lng:.4f}")

        # 2. Filter dealerships by make (case-insensitive, partial match)
        make_mask = self.df['dealer_name'].str.contains(make, case=False, na=False)
        make_dealerships = self.df[make_mask].copy()

        print(f"🏪 Found {len(make_dealerships)} {make} dealerships in database")

        if len(make_dealerships) == 0:
            print(f"❌ No {make} dealerships found in database")
            return []

        # 3. Calculate distances to all dealerships
        nearby_dealerships = []

        for idx, dealership in make_dealerships.iterrows():
            # Skip if missing coordinates
            if pd.isna(dealership['latitude']) or pd.isna(dealership['longitude']):
                continue

            # Calculate distance
            distance = self.haversine_distance(
                user_lat, user_lng,
                float(dealership['latitude']),
                float(dealership['longitude'])
            )

            # Check if within radius
            if distance <= radius_miles:
                dealership_info = {
                    'dealer_name': dealership['dealer_name'],
                    'address': f"{dealership['address_line1']}, {dealership['city']}, {dealership['state']} {dealership['zip_code']}",
                    'city': dealership['city'],
                    'state': dealership['state'],
                    'phone': dealership.get('phone', ''),
                    'website': dealership.get('website', ''),
                    'distance_miles': round(distance, 1),
                    'latitude': float(dealership['latitude']),
                    'longitude': float(dealership['longitude'])
                }
                nearby_dealerships.append(dealership_info)

        # 4. Sort by distance and limit results
        nearby_dealerships.sort(key=lambda x: x['distance_miles'])
        nearby_dealerships = nearby_dealerships[:max_results]

        print(f"✅ Found {len(nearby_dealerships)} {make} dealerships within {radius_miles} miles")

        return nearby_dealerships

    def display_results(self, dealerships: List[Dict]):
        """Display search results in a formatted way"""
        if not dealerships:
            print("No dealerships found.")
            return

        print(f"\n📊 SEARCH RESULTS ({len(dealerships)} dealerships)")
        print("=" * 80)

        for i, dealer in enumerate(dealerships, 1):
            print(f"\n🏪 #{i}: {dealer['dealer_name']}")
            print(f"   📍 {dealer['address']}")
            print(f"   📞 {dealer['phone']}")
            print(f"   🌐 {dealer['website']}")
            print(f"   📏 Distance: {dealer['distance_miles']} miles")

        print("=" * 80)

def find_dealerships_by_distance(make: str, zipcode: str, radius_miles: float, max_results: int = 20) -> List[Dict]:
    """
    Simple interface function to find nearby dealerships

    Args:
        make: Vehicle make ('Jeep', 'Ram', 'Chrysler', etc.)
        zipcode: User zipcode (e.g., '90210')
        radius_miles: Search radius in miles
        max_results: Maximum number of results

    Returns:
        List of dealership dictionaries with distance info
    """
    calculator = DealershipDistanceCalculator()
    return calculator.find_nearby_dealerships(make, zipcode, radius_miles, max_results)

def main():
    """Example usage of the distance calculator"""

    print(f"🚗 DEALERSHIP DISTANCE CALCULATOR")
    print(f"Find dealerships within specified distance from any US zipcode")
    print("=" * 80)

    # Example 1: Jeep dealerships near Beverly Hills
    print(f"\n🔍 EXAMPLE 1: Jeep dealerships near Beverly Hills, CA")
    jeep_dealers = find_dealerships_by_distance("Jeep", "90210", 25, 5)

    if jeep_dealers:
        print(f"✅ Found {len(jeep_dealers)} Jeep dealerships within 25 miles of 90210:")
        for i, dealer in enumerate(jeep_dealers, 1):
            print(f"   {i}. {dealer['dealer_name']} - {dealer['distance_miles']} miles")
            print(f"      📍 {dealer['city']}, {dealer['state']}")

    # Example 2: Ram dealerships near NYC
    print(f"\n🔍 EXAMPLE 2: Ram dealerships near NYC")
    ram_dealers = find_dealerships_by_distance("Ram", "10001", 15, 3)

    if ram_dealers:
        print(f"✅ Found {len(ram_dealers)} Ram dealerships within 15 miles of 10001:")
        for i, dealer in enumerate(ram_dealers, 1):
            print(f"   {i}. {dealer['dealer_name']} - {dealer['distance_miles']} miles")
            print(f"      📞 {dealer['phone']}")

    # Example 3: Interactive search
    print(f"\n" + "="*80)
    print(f"💡 Usage: Use find_dealerships_by_distance(make, zipcode, radius) function")
    print(f"   Example: find_dealerships_by_distance('Chrysler', '60601', 30)")
    print("=" * 80)

if __name__ == "__main__":
    main()