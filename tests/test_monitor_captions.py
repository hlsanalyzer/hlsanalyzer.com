#!/usr/bin/env python3

import pytest
import sys
import os
import time
import uuid
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from monitor_captions import CaptionMonitor, signal_handler


class TestCaptionMonitor:
    
    @pytest.fixture
    def mock_config(self):
        with patch('monitor_captions.Config') as mock_config:
            mock_config.API_KEY = 'test-api-key-123'
            mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
            mock_config.DEFAULT_MONITOR_DURATION = 60
            mock_config.SSE_TIMEOUT = 30
            mock_config.SSE_RECONNECT_DELAY = 5
            yield mock_config
    
    @pytest.fixture
    def caption_monitor(self, mock_config):
        return CaptionMonitor(
            stream_url="https://example.com/test.m3u8",
            duration=30,
            linkid="TEST_LINK_123"
        )
    
    def test_caption_monitor_init_success(self, mock_config):
        monitor = CaptionMonitor(
            stream_url="https://example.com/test.m3u8",
            duration=120,
            linkid="CUSTOM_LINK"
        )
        
        assert monitor.stream_url == "https://example.com/test.m3u8"
        assert monitor.duration == 120
        assert monitor.linkid == "CUSTOM_LINK"
        assert monitor.server_url == "https://hlsanalyzer.com"
        assert monitor.apikey == "test-api-key-123"
        assert monitor.monitoring == False
        assert monitor.stream_added == False
    
    def test_caption_monitor_init_default_values(self, mock_config):
        monitor = CaptionMonitor("https://example.com/stream.m3u8")
        
        assert monitor.duration == 60
        assert monitor.linkid.startswith("CAPTION_MONITOR_")
        assert len(monitor.linkid) == 24  # "CAPTION_MONITOR_" + 8 hex chars
    
    def test_caption_monitor_init_no_api_key(self, mock_config):
        mock_config.API_KEY = None
        
        with pytest.raises(ValueError, match="HLSANALYZER_APIKEY environment variable is not set"):
            CaptionMonitor("https://example.com/test.m3u8")
    
    @patch('monitor_captions.utils.send_command')
    def test_add_stream_success(self, mock_send_command, caption_monitor):
        mock_send_command.return_value = (200, {"status": "success", "message": "Stream added"})
        
        result = caption_monitor.add_stream()
        
        assert result == True
        assert caption_monitor.stream_added == True
        mock_send_command.assert_called_once_with(
            "https://hlsanalyzer.com",
            "test-api-key-123",
            "stream/add",
            ["m3u8=https://example.com/test.m3u8&linkid=TEST_LINK_123"],
            method='POST'
        )
    
    @patch('monitor_captions.utils.send_command')
    def test_add_stream_failure(self, mock_send_command, caption_monitor):
        mock_send_command.return_value = (400, {"error": "Invalid stream"})
        
        result = caption_monitor.add_stream()
        
        assert result == False
        assert caption_monitor.stream_added == False
    
    @patch('monitor_captions.utils.send_command')
    def test_add_stream_exception(self, mock_send_command, caption_monitor):
        mock_send_command.side_effect = Exception("Network error")
        
        result = caption_monitor.add_stream()
        
        assert result == False
        assert caption_monitor.stream_added == False
    
    @patch('monitor_captions.utils.send_command')
    def test_remove_stream_success(self, mock_send_command, caption_monitor):
        caption_monitor.stream_added = True
        mock_send_command.return_value = (200, {"status": "success", "message": "Stream removed"})
        
        result = caption_monitor.remove_stream()
        
        assert result == True
        assert caption_monitor.stream_added == False
        mock_send_command.assert_called_once_with(
            "https://hlsanalyzer.com",
            "test-api-key-123",
            "stream/remove",
            ["m3u8=https://example.com/test.m3u8"],
            method='POST'
        )
    
    @patch('monitor_captions.utils.send_command')
    def test_remove_stream_not_added(self, mock_send_command, caption_monitor):
        caption_monitor.stream_added = False
        
        result = caption_monitor.remove_stream()
        
        assert result == True
        mock_send_command.assert_not_called()
    
    @patch('monitor_captions.utils.send_command')
    def test_remove_stream_failure(self, mock_send_command, caption_monitor):
        caption_monitor.stream_added = True
        mock_send_command.return_value = (404, {"error": "Stream not found"})
        
        result = caption_monitor.remove_stream()
        
        assert result == False
    
    @patch('monitor_captions.requests.get')
    def test_connect_sse_success(self, mock_get, caption_monitor):
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        with patch('monitor_captions.SSEClient') as mock_sse_client:
            mock_client = Mock()
            mock_sse_client.return_value = mock_client
            
            result = caption_monitor.connect_sse()
            
            assert result == mock_client
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "captions/sse" in call_args[0][0]
            assert "apikey=test-api-key-123" in call_args[0][0]
            assert "linkid=TEST_LINK_123" in call_args[0][0]
    
    @patch('monitor_captions.requests.get')
    def test_connect_sse_failure(self, mock_get, caption_monitor):
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")
        
        result = caption_monitor.connect_sse()
        
        assert result is None
    
    def test_process_caption_event_caption(self, caption_monitor):
        mock_event = Mock()
        mock_event.event = 'caption'
        mock_event.data = '  This is a test caption  '
        
        with patch('builtins.print') as mock_print:
            caption_monitor.process_caption_event(mock_event)
            
            mock_print.assert_called()
            call_args = mock_print.call_args[0][0]
            assert "This is a test caption" in call_args
    
    def test_process_caption_event_error(self, caption_monitor):
        mock_event = Mock()
        mock_event.event = 'error'
        mock_event.data = 'Stream disconnected'
        
        with patch('builtins.print') as mock_print:
            caption_monitor.process_caption_event(mock_event)
            
            mock_print.assert_called_with("⚠️ Caption error: Stream disconnected")
    
    def test_process_caption_event_heartbeat(self, caption_monitor):
        mock_event = Mock()
        mock_event.event = 'heartbeat'
        mock_event.data = ''
        
        with patch('builtins.print') as mock_print:
            caption_monitor.process_caption_event(mock_event)
            
            # Heartbeat should not produce output
            mock_print.assert_not_called()
    
    def test_process_caption_event_exception(self, caption_monitor):
        mock_event = Mock()
        mock_event.event = 'caption'
        mock_event.data.strip.side_effect = Exception("Processing error")
        
        with patch('builtins.print') as mock_print:
            caption_monitor.process_caption_event(mock_event)
            
            mock_print.assert_called_with("⚠️ Error processing caption event: Processing error")
    
    @patch('monitor_captions.time.time')
    def test_monitor_captions_timeout(self, mock_time, caption_monitor):
        # Simulate immediate timeout
        mock_time.side_effect = [1000, 1000, 1100, 1100]  # start, check, end, remaining_time calc
        
        with patch.object(caption_monitor, 'connect_sse') as mock_connect:
            with patch('builtins.print'):
                caption_monitor.monitor_captions()
                
                assert caption_monitor.monitoring == False
                mock_connect.assert_called_once()
    
    def test_cleanup(self, caption_monitor):
        caption_monitor.monitoring = True
        
        with patch.object(caption_monitor, 'remove_stream') as mock_remove:
            caption_monitor.cleanup()
            
            assert caption_monitor.monitoring == False
            mock_remove.assert_called_once()


class TestSignalHandler:
    
    @patch('monitor_captions.sys.exit')
    def test_signal_handler_with_monitor(self, mock_exit):
        mock_monitor = Mock()
        
        with patch('monitor_captions.monitor_instance', mock_monitor):
            with patch('builtins.print'):
                signal_handler(2, None)  # SIGINT
                
                mock_monitor.cleanup.assert_called_once()
                mock_exit.assert_called_once_with(0)
    
    @patch('monitor_captions.sys.exit')
    def test_signal_handler_no_monitor(self, mock_exit):
        with patch('monitor_captions.monitor_instance', None):
            with patch('builtins.print'):
                signal_handler(2, None)  # SIGINT
                
                mock_exit.assert_called_once_with(0)


class TestMainFunction:
    
    @patch('monitor_captions.signal.signal')
    @patch('monitor_captions.time.sleep')
    @patch('monitor_captions.sys.argv', ['monitor_captions.py', 'https://example.com/stream.m3u8', '-t', '10'])
    def test_main_success_flow(self, mock_sleep, mock_signal):
        mock_monitor = Mock()
        mock_monitor.add_stream.return_value = True
        
        with patch('monitor_captions.CaptionMonitor', return_value=mock_monitor):
            with patch('monitor_captions.Config') as mock_config:
                mock_config.API_KEY = 'test-key'
                mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
                mock_config.DEFAULT_MONITOR_DURATION = 60
                
                with patch('builtins.print'):
                    # Import and call main function
                    import monitor_captions
                    try:
                        monitor_captions.main()
                    except SystemExit:
                        pass  # Expected from normal execution flow
                
                mock_monitor.add_stream.assert_called_once()
                mock_monitor.monitor_captions.assert_called_once()
                mock_monitor.cleanup.assert_called()
    
    @patch('monitor_captions.signal.signal')
    @patch('monitor_captions.sys.argv', ['monitor_captions.py', 'https://example.com/stream.m3u8'])
    def test_main_add_stream_failure(self, mock_signal):
        mock_monitor = Mock()
        mock_monitor.add_stream.return_value = False
        
        with patch('monitor_captions.CaptionMonitor', return_value=mock_monitor):
            with patch('monitor_captions.Config') as mock_config:
                mock_config.API_KEY = 'test-key'
                mock_config.get_server_url.return_value = 'https://hlsanalyzer.com'
                mock_config.DEFAULT_MONITOR_DURATION = 60
                
                with patch('builtins.print'):
                    import monitor_captions
                    with pytest.raises(SystemExit) as exc_info:
                        monitor_captions.main()
                    
                    assert exc_info.value.code == 1
                
                mock_monitor.add_stream.assert_called_once()
                mock_monitor.monitor_captions.assert_not_called()
    
    @patch('monitor_captions.signal.signal')
    @patch('monitor_captions.sys.argv', ['monitor_captions.py', 'https://example.com/stream.m3u8'])
    def test_main_missing_api_key(self, mock_signal):
        with patch('monitor_captions.CaptionMonitor', side_effect=ValueError("HLSANALYZER_APIKEY environment variable is not set.")):
            with patch('builtins.print'):
                import monitor_captions
                with pytest.raises(SystemExit) as exc_info:
                    monitor_captions.main()
                
                assert exc_info.value.code == 1