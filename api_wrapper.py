#!/usr/bin/env python3
"""
API WRAPPER FOR GEOGRAPHIC FUNCTIONALITY
Provides REST-like interface for UI integration
"""

import json
import time
from typing import Dict, List, Optional
from dealership_distance_calculator import DealershipDistanceCalculator

class DealershipAPI:
    """API wrapper for dealership geographic functionality"""

    def __init__(self):
        self.calculator = DealershipDistanceCalculator()

    def search_dealerships(self,
                          make: str,
                          zipcode: str,
                          radius_miles: float,
                          max_results: int = 20) -> Dict:
        """
        API endpoint: POST /api/v1/dealerships/search

        Returns JSON response suitable for UI consumption
        """
        start_time = time.time()

        try:
            # Validate inputs
            validation_error = self._validate_search_params(make, zipcode, radius_miles, max_results)
            if validation_error:
                return validation_error

            # Geocode user location
            geocoding_start = time.time()
            user_coords = self.calculator.geocode_zipcode(zipcode)
            geocoding_time = (time.time() - geocoding_start) * 1000

            if not user_coords:
                return {
                    "success": False,
                    "error": {
                        "code": "GEOCODING_FAILED",
                        "message": f"Could not geocode zipcode: {zipcode}",
                        "suggestions": ["Check zipcode format", "Try nearby zipcode"]
                    }
                }

            # Search dealerships
            search_start = time.time()
            dealerships = self.calculator.find_nearby_dealerships(
                make=make,
                zipcode=zipcode,
                radius_miles=radius_miles,
                max_results=max_results
            )
            search_time = (time.time() - search_start) * 1000

            if not dealerships:
                return {
                    "success": False,
                    "error": {
                        "code": "NO_DEALERSHIPS_FOUND",
                        "message": f"No {make} dealerships found within {radius_miles} miles of {zipcode}",
                        "suggestions": ["Increase search radius", "Try different vehicle make"]
                    }
                }

            # Format response
            total_time = (time.time() - start_time) * 1000

            return {
                "success": True,
                "user_location": {
                    "zipcode": zipcode,
                    "latitude": user_coords[0],
                    "longitude": user_coords[1],
                    "geocoded_address": f"Zipcode {zipcode}"
                },
                "search_parameters": {
                    "make": make,
                    "radius_miles": radius_miles,
                    "max_results": max_results
                },
                "results": {
                    "total_found": len(dealerships),
                    "dealerships": [self._format_dealership(d) for d in dealerships]
                },
                "performance": {
                    "geocoding_time_ms": int(geocoding_time),
                    "search_time_ms": int(search_time),
                    "total_time_ms": int(total_time)
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e),
                    "suggestions": ["Try again later", "Contact support"]
                }
            }

    def get_available_makes(self) -> Dict:
        """
        API endpoint: GET /api/v1/dealerships/makes

        Returns available vehicle makes with counts
        """
        try:
            df = self.calculator.df

            # Count dealerships by make (approximate - check dealer names)
            make_counts = {}
            makes = ['Jeep', 'Ram', 'Chrysler', 'Dodge']

            for make in makes:
                count = len(df[df['dealer_name'].str.contains(make, case=False, na=False)])
                if count > 0:
                    make_counts[make] = count

            return {
                "success": True,
                "makes": [
                    {"value": make, "label": make, "count": count}
                    for make, count in make_counts.items()
                ]
            }

        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }

    def geocode_zipcode_api(self, zipcode: str) -> Dict:
        """
        API endpoint: GET /api/v1/geocode?zipcode={zipcode}

        Returns coordinates for zipcode
        """
        try:
            coords = self.calculator.geocode_zipcode(zipcode)

            if coords:
                return {
                    "success": True,
                    "zipcode": zipcode,
                    "latitude": coords[0],
                    "longitude": coords[1]
                }
            else:
                return {
                    "success": False,
                    "error": {
                        "code": "GEOCODING_FAILED",
                        "message": f"Could not geocode zipcode: {zipcode}"
                    }
                }

        except Exception as e:
            return {
                "success": False,
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": str(e)
                }
            }

    def _validate_search_params(self, make: str, zipcode: str, radius_miles: float, max_results: int) -> Optional[Dict]:
        """Validate search parameters"""

        # Validate make
        valid_makes = ['jeep', 'ram', 'chrysler', 'dodge']
        if make.lower() not in valid_makes:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_MAKE",
                    "message": f"Invalid make: {make}",
                    "suggestions": [f"Valid makes: {', '.join(valid_makes)}"]
                }
            }

        # Validate zipcode
        if not zipcode or len(zipcode) != 5 or not zipcode.isdigit():
            return {
                "success": False,
                "error": {
                    "code": "INVALID_ZIPCODE",
                    "message": f"Invalid zipcode: {zipcode}",
                    "suggestions": ["Use 5-digit US zipcode (e.g., 90210)"]
                }
            }

        # Validate radius
        if radius_miles < 1 or radius_miles > 500:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_RADIUS",
                    "message": f"Invalid radius: {radius_miles}",
                    "suggestions": ["Use radius between 1 and 500 miles"]
                }
            }

        # Validate max_results
        if max_results < 1 or max_results > 100:
            return {
                "success": False,
                "error": {
                    "code": "INVALID_MAX_RESULTS",
                    "message": f"Invalid max_results: {max_results}",
                    "suggestions": ["Use max_results between 1 and 100"]
                }
            }

        return None

    def _format_dealership(self, dealership: Dict) -> Dict:
        """Format dealership data for API response"""
        return {
            "dealer_name": dealership['dealer_name'],
            "address": dealership['address'],
            "city": dealership['city'],
            "state": dealership['state'],
            "phone": dealership.get('phone', ''),
            "website": dealership.get('website', ''),
            "distance_miles": dealership['distance_miles'],
            "latitude": dealership['latitude'],
            "longitude": dealership['longitude'],
            "contact_form_available": bool(dealership.get('website'))  # Assume available if website exists
        }

def main():
    """Test the API wrapper"""
    api = DealershipAPI()

    print("🔌 DEALERSHIP API WRAPPER TEST")
    print("=" * 50)

    # Test 1: Search dealerships
    print("\n🔍 Test 1: Search Jeep dealerships near Beverly Hills")
    response = api.search_dealerships("Jeep", "90210", 25, 5)
    print(json.dumps(response, indent=2))

    # Test 2: Get available makes
    print("\n🔍 Test 2: Get available makes")
    makes_response = api.get_available_makes()
    print(json.dumps(makes_response, indent=2))

    # Test 3: Geocode zipcode
    print("\n🔍 Test 3: Geocode zipcode")
    geocode_response = api.geocode_zipcode_api("10001")
    print(json.dumps(geocode_response, indent=2))

    # Test 4: Error handling
    print("\n🔍 Test 4: Error handling (invalid zipcode)")
    error_response = api.search_dealerships("Jeep", "99999", 25, 5)
    print(json.dumps(error_response, indent=2))

if __name__ == "__main__":
    main()