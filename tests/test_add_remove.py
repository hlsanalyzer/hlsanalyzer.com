#!/usr/bin/env python3

import pytest
import os
import sys
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import add_remove


class TestAddStream:
    
    @patch('add_remove.utils.send_command')
    @patch('builtins.print')
    def test_add_stream_success(self, mock_print, mock_send_command):
        with patch('add_remove.Config') as mock_config:
            mock_config.API_KEY = 'test-api-key'
            mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
            
            mock_send_command.return_value = (200, {"status": "added"})
            
            result = add_remove.add_stream("https://example.com/test.m3u8", "TEST_LINK")
            
            assert result is True
            mock_send_command.assert_called_once()
            
    @patch('builtins.print')
    def test_add_stream_missing_apikey(self, mock_print):
        with patch('add_remove.Config') as mock_config:
            mock_config.API_KEY = None
            
            result = add_remove.add_stream("https://example.com/test.m3u8")
            
            assert result is False
            mock_print.assert_any_call("Error: HLSANALYZER_APIKEY environment variable is not set.")
            
    @patch('add_remove.utils.send_command')
    @patch('builtins.print')
    def test_add_stream_failure(self, mock_print, mock_send_command):
        with patch('add_remove.Config') as mock_config:
            mock_config.API_KEY = 'test-api-key'
            mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
            
            mock_send_command.return_value = (400, "Bad Request")
            
            result = add_remove.add_stream("https://example.com/test.m3u8")
            
            assert result is False
            mock_print.assert_any_call("❌ Failed to add stream. Code: 400, Result: Bad Request")


class TestRemoveStream:
    
    @patch('add_remove.utils.send_command')
    @patch('builtins.print')
    def test_remove_stream_success(self, mock_print, mock_send_command):
        with patch('add_remove.Config') as mock_config:
            mock_config.API_KEY = 'test-api-key'
            mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
            
            mock_send_command.return_value = (200, {"status": "removed"})
            
            result = add_remove.remove_stream("https://example.com/test.m3u8")
            
            assert result is True
            mock_send_command.assert_called_once()
            
    @patch('builtins.print')
    def test_remove_stream_missing_apikey(self, mock_print):
        with patch('add_remove.Config') as mock_config:
            mock_config.API_KEY = None
            
            result = add_remove.remove_stream("https://example.com/test.m3u8")
            
            assert result is False
            mock_print.assert_any_call("Error: HLSANALYZER_APIKEY environment variable is not set.")
            
    @patch('add_remove.utils.send_command')
    @patch('builtins.print')
    def test_remove_stream_failure(self, mock_print, mock_send_command):
        with patch('add_remove.Config') as mock_config:
            mock_config.API_KEY = 'test-api-key'
            mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
            
            mock_send_command.return_value = (404, "Not Found")
            
            result = add_remove.remove_stream("https://example.com/test.m3u8")
            
            assert result is False
            mock_print.assert_any_call("❌ Failed to remove stream. Code: 404, Result: Not Found")


