#!/usr/local/bin/python3

# MIT License
# Copyright (c) 2021-2025 HLSAnalyzer.com
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import argparse
import sys
import uuid
import utils
from config import Config


def add_stream(stream_url, linkid=None):
    """Add a stream to HLS monitoring"""
    server = Config.get_server_url()
    apikey = Config.API_KEY
    if not apikey:
        print("Error: HLSANALYZER_APIKEY environment variable is not set.")
        return False
    
    if not linkid:
        linkid = f"ADDREMOVE_{uuid.uuid4().hex[:8].upper()}"
    
    print(f"Adding stream: {stream_url}")
    print(f"Link ID: {linkid}")
    
    (code, result) = utils.send_command(server, apikey, "stream/add", [f"m3u8={stream_url}&linkid={linkid}"], method='POST')
    
    if code == 200:
        print(f"✅ Stream added successfully: {result}")
        return True
    else:
        print(f"❌ Failed to add stream. Code: {code}, Result: {result}")
        return False


def remove_stream(stream_url):
    """Remove a stream from HLS monitoring"""
    server = Config.get_server_url()
    apikey = Config.API_KEY
    if not apikey:
        print("Error: HLSANALYZER_APIKEY environment variable is not set.")
        return False
    
    print(f"Removing stream: {stream_url}")
    
    (code, result) = utils.send_command(server, apikey, "stream/remove", [f"m3u8={stream_url}"], method='POST')
    
    if code == 200:
        print(f"✅ Stream removed successfully: {result}")
        return True
    else:
        print(f"❌ Failed to remove stream. Code: {code}, Result: {result}")
        return False




def main():
    parser = argparse.ArgumentParser(
        description='Add or remove HLS streams from monitoring',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a stream
  python add_remove.py add https://example.com/stream.m3u8

  # Add a stream with custom linkid  
  python add_remove.py add https://example.com/stream.m3u8 --linkid MY_STREAM

  # Remove a stream
  python add_remove.py remove https://example.com/stream.m3u8
        """
    )
    
    parser.add_argument('action', choices=['add', 'remove'],
                       help='Action to perform: add stream or remove stream')
    parser.add_argument('stream_url', 
                       help='HLS stream URL')
    parser.add_argument('--linkid',
                       help='Custom link ID for the stream (optional for add)')
    
    args = parser.parse_args()
    
    if args.action == 'add':
        add_stream(args.stream_url, args.linkid)
    elif args.action == 'remove':
        remove_stream(args.stream_url)


if __name__ == '__main__':
    main()
