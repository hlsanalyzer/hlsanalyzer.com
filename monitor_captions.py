#!/usr/bin/env python3

# MIT License
# Copyright (c) 2025 HLSAnalyzer.com
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import signal
import sys
import time
import threading
from datetime import datetime, timedelta
import uuid
import requests
from sseclient import SSEClient
from urllib.parse import urljoin

from config import Config
import utils


class CaptionMonitor:
    """Monitor HLS stream for 608 captions using SSE"""
    
    def __init__(self, stream_url, duration=None, linkid=None):
        self.stream_url = stream_url
        self.duration = duration or Config.DEFAULT_MONITOR_DURATION
        self.linkid = linkid or f"CAPTION_MONITOR_{uuid.uuid4().hex[:8].upper()}"
        
        # Validate server URL
        try:
            self.server_url = Config.get_server_url()
        except ValueError as e:
            raise ValueError(str(e))
            
        self.apikey = Config.API_KEY
        self.monitoring = False
        self.stream_added = False
        self.variant_linkids = []  # Store variant link IDs for caption monitoring
        self.caption_linkid = None  # Selected variant linkid for caption monitoring
        
        # Validate API key
        if not self.apikey:
            raise ValueError("Error: HLSANALYZER_APIKEY environment variable is not set.")
    
    def add_stream(self):
        """Add stream to HLSAnalyzer monitoring"""
        print(f"Adding stream to monitoring: {self.stream_url}")
        print(f"Link ID: {self.linkid}")
        
        try:
            params = [f"m3u8={self.stream_url}&linkid={self.linkid}"]
            code, result = utils.send_command(
                self.server_url, 
                self.apikey, 
                "stream/add", 
                params, 
                method='POST'
            )
            
            if code == 200:
                print(f"✅ Stream added successfully: {result}")
                self.stream_added = True
                
                # Parse variants if this is a master playlist
                if isinstance(result, dict) and 'variants' in result and result['variants'] is not None:
                    # Select the first variant for caption monitoring
                    self.variant_linkids = list(result['variants'].keys())
                    if self.variant_linkids:
                        self.caption_linkid = self.variant_linkids[0]
                        print(f"📺 Found {len(self.variant_linkids)} variants, using first: {self.caption_linkid}")
                    else:
                        self.caption_linkid = self.linkid
                        print("⚠️ No variants found, using master linkid")
                else:
                    # Single media playlist - use the main linkid
                    self.caption_linkid = self.linkid
                    print(f"📺 Single media playlist, using linkid: {self.linkid}")
                
                return True
            else:
                print(f"❌ Failed to add stream. Code: {code}, Result: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Error adding stream: {e}")
            return False
    
    def remove_stream(self):
        """Remove stream from HLSAnalyzer monitoring"""
        if not self.stream_added:
            return True
            
        print(f"\nRemoving stream from monitoring...")
        
        try:
            params = [f"m3u8={self.stream_url}"]
            code, result = utils.send_command(
                self.server_url,
                self.apikey,
                "stream/remove",
                params,
                method='POST'
            )
            
            if code == 200:
                print(f"✅ Stream removed successfully: {result}")
                self.stream_added = False
                return True
            else:
                print(f"⚠️ Warning: Failed to remove stream. Code: {code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Warning: Error removing stream: {e}")
            return False
    
    def connect_sse(self):
        """Connect to SSE endpoint for caption monitoring"""
        # Construct SSE URL for captions using the selected variant linkid
        caption_linkid = self.caption_linkid if self.caption_linkid is not None else self.linkid
        sse_url = urljoin(self.server_url, f"/api/stream/captions/sse?apikey={self.apikey}&linkid={caption_linkid}")
        
        print(f"Connecting to SSE endpoint for captions...")
        print(f"URL: {sse_url}")
        print(f"Duration: {self.duration} seconds")
        print("Press Ctrl+C to stop monitoring early\n")
        
        try:
            headers = {
                'Accept': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'User-Agent': 'HLSAnalyzer-Caption-Monitor/1.0'
            }
            
            # Create SSE client with timeout
            response = requests.get(
                sse_url, 
                headers=headers, 
                stream=True, 
                timeout=Config.SSE_TIMEOUT
            )
            response.raise_for_status()
            
            client = SSEClient(response)
            return client
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to connect to SSE endpoint: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error connecting to SSE: {e}")
            return None
    
    def process_caption_event(self, event):
        """Process and display caption event"""
        try:
            if event.event == 'message':
                try:
                    import json
                    data = json.loads(event.data)
                    
                    if data.get('status') == 'connected':
                        print(f"🔗 Connected to linkid: {data.get('linkid')}")
                    elif data.get('status') == 'no_captions_yet':
                        pass  # Don't spam with no captions messages
                    elif 'initial_captions' in data:
                        # Initial captions when catching up
                        captions = data['initial_captions']
                        for caption in captions:
                            content = caption.get('content', '').strip()
                            if content:
                                print(content)
                    elif 'new_captions' in data:
                        # New real-time captions
                        captions = data['new_captions']
                        for caption in captions:
                            content = caption.get('content', '').strip()
                            if content:
                                print(content)
                    elif 'content' in data:
                        # Single caption content
                        caption_content = data['content'].strip()
                        if caption_content:
                            print(caption_content)
                    else:
                        # Print any other message types for debugging
                        print(f"📝 SSE Message: {data}")
                        
                except json.JSONDecodeError:
                    # If it's not JSON, print as-is
                    print(f"📝 Raw message: {event.data}")
                    
            elif event.event == 'caption':
                caption_data = event.data.strip()
                if caption_data:
                    print(caption_data)
                
            elif event.event == 'heartbeat':
                # Optional: show heartbeat for connection health
                pass
                
            elif event.event == 'error':
                print(f"⚠️ Caption error: {event.data}")
            
            else:
                print(f"❓ Unknown event type: {event.event} - Data: {event.data}")
                
        except Exception as e:
            print(f"⚠️ Error processing caption event: {e}")
    
    def monitor_captions(self):
        """Main caption monitoring loop"""
        self.monitoring = True
        start_time = time.time()
        end_time = start_time + self.duration
        reconnect_attempts = 0
        max_reconnects = 3
        
        print("🎬 Starting caption monitoring...")
        
        while self.monitoring and time.time() < end_time:
            try:
                client = self.connect_sse()
                if not client:
                    print("❌ Failed to establish SSE connection")
                    break
                
                print("✅ Connected to caption stream")
                reconnect_attempts = 0
                
                # Monitor events until timeout or disconnection
                for event in client.events():
                    if not self.monitoring or time.time() >= end_time:
                        break
                        
                    self.process_caption_event(event)
                
            except KeyboardInterrupt:
                print("\n⏹️ Monitoring stopped by user")
                break
                
            except Exception as e:
                print(f"⚠️ Connection lost: {e}")
                reconnect_attempts += 1
                
                if reconnect_attempts <= max_reconnects and self.monitoring:
                    print(f"🔄 Reconnecting in {Config.SSE_RECONNECT_DELAY} seconds... (attempt {reconnect_attempts}/{max_reconnects})")
                    time.sleep(Config.SSE_RECONNECT_DELAY)
                else:
                    print("❌ Max reconnection attempts reached")
                    break
        
        remaining_time = end_time - time.time()
        if remaining_time <= 0 and self.monitoring:
            print(f"\n⏰ Monitoring completed after {self.duration} seconds")
        
        self.monitoring = False
    
    def cleanup(self):
        """Cleanup resources and remove stream"""
        self.monitoring = False
        self.remove_stream()


# Global monitor instance for signal handling
monitor_instance = None

def signal_handler(signum, frame):
    """Handle Ctrl+C gracefully"""
    global monitor_instance
    print("\n⏹️ Received interrupt signal, shutting down...")
    
    if monitor_instance:
        monitor_instance.cleanup()
    
    sys.exit(0)


def main():
    global monitor_instance
    
    parser = argparse.ArgumentParser(
        description="Monitor HLS stream for 608 captions using SSE",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s https://example.com/stream.m3u8
  %(prog)s https://example.com/stream.m3u8 -t 120
  %(prog)s https://example.com/stream.m3u8 --linkid MY_STREAM_01
        """
    )
    
    parser.add_argument(
        'stream_url',
        help='HLS stream URL to monitor for captions'
    )
    
    parser.add_argument(
        '-t', '--time',
        type=int,
        default=Config.DEFAULT_MONITOR_DURATION,
        help=f'Duration in seconds (default: {Config.DEFAULT_MONITOR_DURATION})'
    )
    
    parser.add_argument(
        '--linkid',
        help='Custom link ID for the stream (optional)'
    )
    
    args = parser.parse_args()
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Create caption monitor
        monitor_instance = CaptionMonitor(
            stream_url=args.stream_url,
            duration=args.time,
            linkid=args.linkid
        )
        
        # Add stream to monitoring
        if not monitor_instance.add_stream():
            print("❌ Failed to add stream. Exiting.")
            sys.exit(1)
        
        # Wait a moment for stream to initialize
        print("⏳ Waiting for stream initialization...")
        time.sleep(3)
        
        # Start caption monitoring
        monitor_instance.monitor_captions()
        
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
        
    finally:
        # Cleanup
        if monitor_instance:
            monitor_instance.cleanup()


if __name__ == '__main__':
    main()
