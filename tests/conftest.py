#!/usr/bin/env python3

import pytest
import os
import sys
from unittest.mock import Mock

# Add parent directory to path so tests can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


@pytest.fixture
def mock_api_response():
    """Sample API status response for testing"""
    return {
        'status': {
            'https://example.com/master.m3u8': {
                'Errors': 1,
                'Warnings': 2,
                'Timestamp': 1234567890,
                'LinkID': 'master-link-1',
                'Variants': {
                    'https://example.com/variant1.m3u8': {
                        'Errors': 0,
                        'Warnings': 1,
                        'Timestamp': 1234567890,
                        'LinkID': 'variant-link-1'
                    },
                    'https://example.com/variant2.m3u8': {
                        'Errors': 2,
                        'Warnings': 0,
                        'Timestamp': 1234567890,
                        'LinkID': 'variant-link-2'
                    }
                }
            },
            'https://example.com/single.m3u8': {
                'Errors': 0,
                'Warnings': 0,
                'Timestamp': 1234567890,
                'LinkID': 'single-link-1'
            }
        }
    }


@pytest.fixture
def mock_scte35_records():
    """Sample SCTE-35 records for testing"""
    return [
        {
            "timestamp": 1234567890,
            "scte35": "SCTE-35 Cue Out 30.0 seconds"
        },
        {
            "timestamp": 1234567920,
            "scte35": "SCTE-35 Cue In 30.5 seconds"
        },
        {
            "timestamp": 1234567950,
            "scte35": "SCTE-35 Program End"
        }
    ]


@pytest.fixture
def mock_alert_records():
    """Sample alert records for testing"""
    return [
        {
            "timestamp": 1234567890,
            "alerts": "STREAM OUTAGE ALERT detected for 5 minutes"
        },
        {
            "timestamp": 1234567920,
            "alerts": "SCTE-35 ALERT CLEARED after 30 seconds"
        },
        {
            "timestamp": 1234567950,
            "alerts": "STREAM ALERT CLEARED after 2 minutes"
        }
    ]


@pytest.fixture
def mock_error_records():
    """Sample error records for testing"""
    return [
        {
            "timestamp": 1234567890,
            "error": "Segment download timeout"
        },
        {
            "timestamp": 1234567920,
            "error": "Invalid playlist format"
        }
    ]


@pytest.fixture
def mock_warning_records():
    """Sample warning records for testing"""
    return [
        {
            "timestamp": 1234567890,
            "warning": "Segment duration variance high"
        },
        {
            "timestamp": 1234567920,
            "warning": "Bitrate fluctuation detected"
        }
    ]


@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing"""
    mock_db = Mock()
    mock_cursor = Mock()
    mock_db.cursor.return_value = mock_cursor
    return mock_db, mock_cursor


@pytest.fixture
def sample_environment():
    """Sample environment variables for testing"""
    return {
        'APIKEY': 'test-api-key-12345',
        'DBHOST': 'localhost',
        'DBUSER': 'testuser',
        'DBPW': 'testpassword'
    }


@pytest.fixture(autouse=True)
def clean_environment():
    """Ensure clean environment for each test"""
    # Store original environment
    original_env = os.environ.copy()
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)