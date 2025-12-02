#!/usr/bin/env python3

import pytest
import json
import urllib.error
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import utils


class TestGetRecords:
    
    def test_get_records_success(self):
        mock_response = {"records": [{"timestamp": 123, "data": "test"}]}
        
        with patch.object(utils, 'load_from_uri', return_value=json.dumps(mock_response)):
            result = utils.get_records("https://test.com", "api-key", "link123", 100, 200, "errors")
            
            assert result == mock_response
            utils.load_from_uri.assert_called_once_with(
                "https://test.com/api/errors?apikey=api-key&start=100&end=200&linkid=link123"
            )
    
    def test_get_records_http_error(self):
        with patch.object(utils, 'load_from_uri', side_effect=urllib.error.HTTPError(
            url="test", code=404, msg="Not Found", hdrs={}, fp=Mock()
        )):
            with patch('builtins.print'):
                result = utils.get_records("https://test.com", "api-key", "link123", 100, 200, "errors")
                
                assert result is None
    
    def test_get_records_general_exception(self):
        with patch.object(utils, 'load_from_uri', side_effect=Exception("Network error")):
            with patch('builtins.print'):
                result = utils.get_records("https://test.com", "api-key", "link123", 100, 200, "errors")
                
                assert result is None


class TestSendCommand:
    
    def test_send_command_success_no_params(self):
        mock_response = {"status": "success"}
        
        with patch.object(utils, 'load_from_uri', return_value=json.dumps(mock_response)):
            with patch('builtins.print'):
                code, result = utils.send_command("https://test.com", "api-key", "status")
                
                assert code == 200
                assert result == mock_response
    
    def test_send_command_success_with_params(self):
        mock_response = {"status": "added"}
        
        with patch.object(utils, 'load_from_uri', return_value=json.dumps(mock_response)):
            with patch('builtins.print'):
                code, result = utils.send_command(
                    "https://test.com", "api-key", "stream/add", 
                    ["m3u8=test.m3u8", "linkid=test123"], "POST"
                )
                
                assert code == 200
                assert result == mock_response
    
    def test_send_command_http_error(self):
        mock_error = urllib.error.HTTPError(
            url="test", code=400, msg="Bad Request", hdrs={}, fp=Mock()
        )
        mock_read_result = Mock()
        mock_read_result.decode.return_value = "Error details"
        mock_error.read.return_value = mock_read_result
        
        with patch.object(utils, 'load_from_uri', side_effect=mock_error):
            with patch('builtins.print'):
                code, result = utils.send_command("https://test.com", "api-key", "invalid")
                
                assert code == 400
                assert result is None
    
    def test_send_command_general_exception(self):
        with patch.object(utils, 'load_from_uri', side_effect=Exception("Network error")):
            with patch('builtins.print'):
                code, result = utils.send_command("https://test.com", "api-key", "status")
                
                assert code == 500
                assert result is None


class TestLoadFromUri:
    
    @patch('utils.build_opener')
    @patch('utils.install_opener')
    def test_load_from_uri_success(self, mock_install, mock_build):
        mock_resource = Mock()
        mock_resource.read.side_effect = [b'{"test": true}', b'']
        mock_resource.headers.get_content_charset.return_value = "utf-8"
        
        mock_opener = Mock()
        mock_opener.open.return_value = mock_resource
        mock_build.return_value = mock_opener
        
        result = utils.load_from_uri("https://test.com")
        
        assert result == '{"test": true}'
        mock_opener.open.assert_called_once()
    
    @patch('utils.build_opener')
    @patch('utils.install_opener')
    def test_load_from_uri_with_custom_method(self, mock_install, mock_build):
        mock_resource = Mock()
        mock_resource.read.side_effect = [b'response', b'']
        mock_resource.headers.get_content_charset.return_value = "utf-8"
        
        mock_opener = Mock()
        mock_opener.open.return_value = mock_resource
        mock_build.return_value = mock_opener
        
        with patch('utils.Request') as mock_request:
            utils.load_from_uri("https://test.com", method="POST", timeout=30)
            
            mock_request.assert_called_once_with("https://test.com", method="POST")


class TestGetAllStatus:
    
    def test_get_all_status_success(self):
        mock_response = {
            "status": {
                "stream1": {"LinkID": "abc", "Errors": 0, "Warnings": 1}
            }
        }
        
        with patch.object(utils, 'load_from_uri', return_value=json.dumps(mock_response)):
            result = utils.get_all_status("https://test.com", "api-key")
            
            assert result == mock_response
            utils.load_from_uri.assert_called_once_with(
                "https://test.com/api/status?apikey=api-key"
            )
    
    def test_get_all_status_http_error(self):
        mock_error = urllib.error.HTTPError(
            url="test", code=401, msg="Unauthorized", hdrs={}, fp=Mock()
        )
        mock_read_result = Mock()
        mock_read_result.decode.return_value = "Unauthorized"
        mock_error.read.return_value = mock_read_result
        
        with patch.object(utils, 'load_from_uri', side_effect=mock_error):
            with patch('builtins.print'):
                result = utils.get_all_status("https://test.com", "invalid-key")
                
                assert result is None
    
    def test_get_all_status_general_exception(self):
        with patch.object(utils, 'load_from_uri', side_effect=Exception("Network error")):
            with patch('builtins.print'):
                result = utils.get_all_status("https://test.com", "api-key")
                
                assert result is None


class TestReadPython3x:
    
    def test_read_python3x_success(self):
        mock_resource = Mock()
        mock_resource.read.side_effect = [b'Hello ', b'World', b'']
        mock_resource.headers.get_content_charset.return_value = "utf-8"
        
        result = utils._read_python3x(mock_resource)
        
        assert result == "Hello World"
    
    def test_read_python3x_with_charset(self):
        mock_resource = Mock()
        mock_resource.read.side_effect = [b'\xc3\xa9', b'']  # é in UTF-8
        mock_resource.headers.get_content_charset.return_value = "utf-8"
        
        result = utils._read_python3x(mock_resource)
        
        assert result == "é"
    
    def test_read_python3x_fallback_charset(self):
        mock_resource = Mock()
        mock_resource.read.side_effect = [b'test', b'']
        mock_resource.headers.get_content_charset.return_value = "utf-8"
        
        result = utils._read_python3x(mock_resource)
        
        assert result == "test"