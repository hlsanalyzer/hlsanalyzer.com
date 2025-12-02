#!/usr/bin/env python3

import pytest
import os
import sys
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import get_all_errors


class TestProcessLinkStatus:
    
    def test_process_link_status_success(self):
        link_status = {
            'Errors': 5,
            'Warnings': 3,
            'Timestamp': 1234567890,
            'LinkID': 'test-link-123'
        }
        
        error_count, warning_count, timestamp, linkid = get_all_errors.process_link_status(link_status)
        
        assert error_count == 5
        assert warning_count == 3
        assert timestamp == 1234567890
        assert linkid == 'test-link-123'
    
    def test_process_link_status_zero_counts(self):
        link_status = {
            'Errors': 0,
            'Warnings': 0,
            'Timestamp': 9876543210,
            'LinkID': 'another-link'
        }
        
        error_count, warning_count, timestamp, linkid = get_all_errors.process_link_status(link_status)
        
        assert error_count == 0
        assert warning_count == 0
        assert timestamp == 9876543210
        assert linkid == 'another-link'


class TestGetAllErrors:
    
    @patch('get_all_errors.utils.get_all_status')
    @patch('get_all_errors.utils.get_records')
    @patch('builtins.print')
    def test_get_all_errors_media_playlist_with_errors(self, mock_print, mock_get_records, mock_get_status):
        with patch('get_all_errors.Config') as mock_config:
            mock_config.API_KEY = 'test-api-key'
            mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
            
            mock_status_response = {
                'status': {
                    'https://example.com/stream.m3u8': {
                        'Errors': 2,
                        'Warnings': 1,
                        'Timestamp': 1234567890,
                        'LinkID': 'media-link-1'
                    }
                }
            }
            mock_get_status.return_value = mock_status_response
            mock_get_records.return_value = [{"error": "test error"}]
            
            get_all_errors.get_all_errors()
            
            mock_get_status.assert_called_once_with("https://hlsanalyzer.com", "test-api-key")
            
            # Should call get_records for both errors and warnings
            assert mock_get_records.call_count == 2
            
            # Check error records call
            error_call = mock_get_records.call_args_list[0]
            assert error_call[0][:5] == ("https://hlsanalyzer.com", "test-api-key", "media-link-1", 0, 1234567890)
            assert error_call[1]['mode'] == "stream/errors"
            
            # Check warning records call
            warning_call = mock_get_records.call_args_list[1]
            assert warning_call[0][:5] == ("https://hlsanalyzer.com", "test-api-key", "media-link-1", 0, 1234567890)
            assert warning_call[1]['mode'] == "stream/warnings"
            
            # Check print outputs
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("MEDIA [https://example.com/stream.m3u8]" in call for call in print_calls)
    
    @patch('get_all_errors.utils.get_all_status')
    @patch('get_all_errors.utils.get_records')
    @patch('builtins.print')
    def test_get_all_errors_master_playlist_with_variants(self, mock_print, mock_get_records, mock_get_status):
        with patch('get_all_errors.Config') as mock_config:
            mock_config.API_KEY = 'test-api-key'
            mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
            
            mock_status_response = {
                'status': {
                    'https://example.com/master.m3u8': {
                        'Errors': 1,
                        'Warnings': 0,
                        'Timestamp': 1234567890,
                        'LinkID': 'master-link-1',
                        'Variants': {
                            'variant1': {
                                'Errors': 3.0,
                                'Warnings': 2.0,
                                'Timestamp': 1234567890,
                                'LinkID': 'variant-link-1'
                            },
                            'variant2': {
                                'Errors': 0.0,
                                'Warnings': 0.0,
                                'Timestamp': 1234567890,
                                'LinkID': 'variant-link-2'
                            }
                        }
                    }
                }
            }
            mock_get_status.return_value = mock_status_response
            mock_get_records.return_value = [{"error": "test error"}]
            
            get_all_errors.get_all_errors()
            
            mock_get_status.assert_called_once_with("https://hlsanalyzer.com", "test-api-key")
            
            # Should call get_records 3 times: 1 for master errors, 2 for variant1 (errors + warnings)
            assert mock_get_records.call_count == 3
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("MASTER [https://example.com/master.m3u8]" in call for call in print_calls)
            assert any("|-- Variant [variant1]" in call for call in print_calls)
            assert any("|-- Variant [variant2]" in call for call in print_calls)
    
    @patch('get_all_errors.utils.get_all_status')
    @patch('get_all_errors.utils.get_records')
    @patch('builtins.print')
    def test_get_all_errors_no_errors_or_warnings(self, mock_print, mock_get_records, mock_get_status):
        with patch('get_all_errors.Config') as mock_config:
            mock_config.API_KEY = 'test-api-key'
            mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
            
            mock_status_response = {
                'status': {
                    'https://example.com/clean.m3u8': {
                        'Errors': 0,
                        'Warnings': 0,
                        'Timestamp': 1234567890,
                        'LinkID': 'clean-link'
                    }
                }
            }
            mock_get_status.return_value = mock_status_response
            
            get_all_errors.get_all_errors()
            
            # Should not call get_records since no errors or warnings
            assert mock_get_records.call_count == 0
            
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            assert any("MEDIA [https://example.com/clean.m3u8]" in call for call in print_calls)
    
    @patch('builtins.print')
    def test_get_all_errors_missing_apikey(self, mock_print):
        with patch('get_all_errors.Config') as mock_config:
            mock_config.API_KEY = None
            
            result = get_all_errors.get_all_errors()
            
            assert result is None
            mock_print.assert_called_once_with("Error: HLSANALYZER_APIKEY environment variable is not set.")
    
    @patch('get_all_errors.utils.get_all_status')
    @patch('builtins.print')
    def test_get_all_errors_status_api_returns_none(self, mock_print, mock_get_status):
        with patch('get_all_errors.Config') as mock_config:
            mock_config.API_KEY = 'test-api-key'
            mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
            mock_get_status.return_value = None
            
            get_all_errors.get_all_errors()
            
            # Function should handle None response gracefully and not crash
            mock_get_status.assert_called_once_with("https://hlsanalyzer.com", "test-api-key")
    
    @patch('get_all_errors.utils.get_all_status')
    @patch('get_all_errors.utils.get_records')
    @patch('builtins.print')
    def test_get_all_errors_string_error_counts(self, mock_print, mock_get_records, mock_get_status):
        with patch('get_all_errors.Config') as mock_config:
            mock_config.API_KEY = 'test-api-key'
            mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
            
            """Test that string error counts are properly converted to int/float"""
            mock_status_response = {
                'status': {
                    'https://example.com/stream.m3u8': {
                        'Errors': "2.5",  # String that converts to float > 0
                        'Warnings': "0",   # String that converts to 0
                        'Timestamp': 1234567890,
                        'LinkID': 'string-link'
                    }
                }
            }
            mock_get_status.return_value = mock_status_response
            mock_get_records.return_value = []
            
            get_all_errors.get_all_errors()
            
            # Should call get_records for errors (since int(float("2.5")) > 0) but not warnings
            assert mock_get_records.call_count == 1
            error_call = mock_get_records.call_args_list[0]
            assert error_call[1]['mode'] == "stream/errors"