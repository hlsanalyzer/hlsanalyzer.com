"""
Configuration module for HLSAnalyzer API client
"""

import os

class Config:
    """Configuration settings for HLSAnalyzer API operations"""
    
    # API Configuration
    SERVER_URL = os.environ.get('HLSANALYZER_SERVER')
    API_KEY = os.environ.get('HLSANALYZER_APIKEY')
    DEFAULT_TIMEOUT = 20
    SEGMENT_DOWNLOAD_TIMEOUT = 5
    
    # SSE Configuration
    SSE_TIMEOUT = 30
    SSE_RECONNECT_DELAY = 5
    DEFAULT_MONITOR_DURATION = 60
    
    # Database Configuration
    INTERVAL_MINUTES = 400  # Update interval for database operations
    MAX_DB_NAME_LENGTH = 64
    
    # Test Stream Configuration
    TEST_STREAM_URL = "https://bitdash-a.akamaihd.net/content/sintel/hls/video/500kbit.m3u8"
    TEST_LINK_ID = "STREAMTEST"
    
    # Database Environment Variables
    DB_HOST = os.environ.get('DBHOST')
    DB_USER = os.environ.get('DBUSER')
    DB_PASSWORD = os.environ.get('DBPW')
    
    @classmethod
    def get_server_url(cls):
        """Get the server URL with validation"""
        if not cls.SERVER_URL:
            raise ValueError("Error: HLSANALYZER_SERVER environment variable is not set.")
        return cls.SERVER_URL
    
    @classmethod
    def validate_environment(cls):
        """Validate that required environment variables are set"""
        missing_vars = []
        
        if not cls.API_KEY:
            missing_vars.append('HLSANALYZER_APIKEY')
        if not cls.DB_HOST:
            missing_vars.append('DBHOST')
        if not cls.DB_USER:
            missing_vars.append('DBUSER')
        if not cls.DB_PASSWORD:
            missing_vars.append('DBPW')
            
        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def get_database_config(cls):
        """Get database connection configuration"""
        return {
            'host': cls.DB_HOST,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD
        }
