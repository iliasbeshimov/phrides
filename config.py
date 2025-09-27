#!/usr/bin/env python3
"""
SECURE CONFIGURATION MODULE
Loads API keys and settings from environment variables
"""

import os
from typing import Optional

def load_env_file(env_path: str = '.env'):
    """Load environment variables from .env file if it exists"""
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Load .env file if available
load_env_file()

class Config:
    """Secure configuration class using environment variables"""

    # Google Maps API (for geocoding and mapping)
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv('GOOGLE_MAPS_API_KEY')

    # Mapbox API (for advanced mapping features)
    MAPBOX_ACCESS_TOKEN: Optional[str] = os.getenv('MAPBOX_ACCESS_TOKEN')

    # Census.gov API (usually no key required)
    CENSUS_API_KEY: Optional[str] = os.getenv('CENSUS_API_KEY')

    # Browser automation settings
    HEADLESS_MODE: bool = os.getenv('HEADLESS_MODE', 'true').lower() == 'true'
    BROWSER_TIMEOUT: int = int(os.getenv('BROWSER_TIMEOUT', '30000'))

    # Database settings
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///dealerships.db')

    # Development settings
    DEBUG: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')

    @classmethod
    def validate_required_keys(cls):
        """Validate that required API keys are present"""
        missing_keys = []

        # Only validate keys that are actually needed
        # Census.gov doesn't require a key, so we don't check it

        if cls.GOOGLE_MAPS_API_KEY is None:
            print("⚠️  Warning: GOOGLE_MAPS_API_KEY not set (optional for current functionality)")

        if cls.MAPBOX_ACCESS_TOKEN is None:
            print("⚠️  Warning: MAPBOX_ACCESS_TOKEN not set (optional for current functionality)")

        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")

    @classmethod
    def get_google_maps_key(cls) -> str:
        """Get Google Maps API key with validation"""
        if not cls.GOOGLE_MAPS_API_KEY:
            raise ValueError(
                "Google Maps API key is required. Please set GOOGLE_MAPS_API_KEY environment variable."
            )
        return cls.GOOGLE_MAPS_API_KEY

    @classmethod
    def get_mapbox_token(cls) -> str:
        """Get Mapbox access token with validation"""
        if not cls.MAPBOX_ACCESS_TOKEN:
            raise ValueError(
                "Mapbox access token is required. Please set MAPBOX_ACCESS_TOKEN environment variable."
            )
        return cls.MAPBOX_ACCESS_TOKEN

# Example usage:
def example_usage():
    """Example of how to use the secure configuration"""

    # Validate configuration on startup
    Config.validate_required_keys()

    # Use API keys securely
    try:
        google_key = Config.get_google_maps_key()
        print(f"✅ Google Maps API key loaded (ends with: ...{google_key[-4:]})")
    except ValueError as e:
        print(f"⚠️  {e}")

    try:
        mapbox_token = Config.get_mapbox_token()
        print(f"✅ Mapbox token loaded (ends with: ...{mapbox_token[-4:]})")
    except ValueError as e:
        print(f"⚠️  {e}")

    print(f"🔧 Browser headless mode: {Config.HEADLESS_MODE}")
    print(f"🔧 Browser timeout: {Config.BROWSER_TIMEOUT}ms")

if __name__ == "__main__":
    example_usage()