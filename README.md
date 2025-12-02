# HLSAnalyzer.com API Sample Code

HLSAnalyzer.com is a service that allows continuous monitoring of live HLS streams. The monitoring service is performed using a dedicated real-time monitoring instance, along with a browser-based interface for reviewing stream status and examining various aspects of HLS validation. HLSAnalyzer downloads all segments and playlists for each HLS variant. Master playlists are downloaded every 30 seconds and processed for media playlist changes. Alerts are configurable to report slow delivery of streams (or complete outages) as well as the recovery time, via email and HTTP POSTs.

The monitoring service has a browser-based interface along with an HTTP-based API which enables programmatic interaction with the monitoring instance. This repository provides examples of how to interact with the API. The complete API documentation can be found here: [https://hlsanalyzer.com/api/documentation](https://hlsanalyzer.com/api/documentation)

## Prerequisites

### Environment Variables

All scripts require the following environment variable:

**Required:**
- `HLSANALYZER_APIKEY`: Your HLSAnalyzer API key

**Optional:**
- `HLSANALYZER_SERVER`: Server URL (default: https://hlsanalyzer.com)

### Setting Environment Variables

#### Linux/macOS (Terminal)
```bash
# Set for current session
export HLSANALYZER_APIKEY="your-api-key-here"
export HLSANALYZER_SERVER="https://hlsanalyzer.com"  # optional

# Set permanently (add to ~/.bashrc, ~/.zshrc, or ~/.profile)
echo 'export HLSANALYZER_APIKEY="your-api-key-here"' >> ~/.bashrc
```

#### Windows (Command Prompt)
```cmd
# Set for current session
set HLSANALYZER_APIKEY=your-api-key-here
set HLSANALYZER_SERVER=https://hlsanalyzer.com

# Set permanently
setx HLSANALYZER_APIKEY "your-api-key-here"
```

#### Windows (PowerShell)
```powershell
# Set for current session
$env:HLSANALYZER_APIKEY="your-api-key-here"
$env:HLSANALYZER_SERVER="https://hlsanalyzer.com"

# Set permanently
[Environment]::SetEnvironmentVariable("HLSANALYZER_APIKEY", "your-api-key-here", "User")
```

### Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Available Scripts

### 1. Stream Management (`add_remove.py`)

Add or remove HLS streams from monitoring.

#### Usage Examples:
```bash
# Add a stream
python add_remove.py add https://example.com/stream.m3u8

# Add with custom linkid  
python add_remove.py add https://example.com/stream.m3u8 --linkid MY_STREAM

# Remove a stream
python add_remove.py remove https://example.com/stream.m3u8

# Test add/remove cycle with default test stream
python add_remove.py test
```

#### Features:
- Add any HLS stream URL to monitoring
- Remove streams from monitoring
- Auto-generate unique link IDs
- Test functionality with default streams

### 2. Real-time Caption Monitoring (`monitor_captions.py`)

Monitor 608 captions from HLS streams in real-time using Server-Sent Events (SSE).

#### Usage Examples:
```bash
# Monitor captions for 60 seconds (default)
python monitor_captions.py https://example.com/stream.m3u8

# Monitor for 2 minutes
python monitor_captions.py https://example.com/stream.m3u8 -t 120

# Use custom link ID
python monitor_captions.py https://example.com/stream.m3u8 --linkid MY_STREAM_01
```

#### Features:
- **Real-time Caption Display**: Live 608 caption data via SSE
- **Flexible Duration**: Configurable monitoring time or Ctrl+C to stop
- **Variant Selection**: Automatically selects first variant from master playlists
- **Automatic Reconnection**: Reconnects if SSE connection drops (max 3 attempts)
- **Graceful Cleanup**: Automatically removes streams on exit

#### Output Format:
```
✅ Stream added successfully
🔗 Connected to linkid: 8e0f7d78cf34
📺 Found 3 variants, using first: 8e0f7d78cf34
🎬 Starting caption monitoring...

1
00:00:03,838 --> 00:00:07,706
Welcome to our live broadcast

2
00:00:07,842 --> 00:00:12,711
Today's weather forecast shows...
```

### 3. Error Analysis (`get_all_errors.py`)

Retrieve and analyze errors from all monitored streams.

#### Usage:
```bash
python get_all_errors.py
```

#### Features:
- Get comprehensive error reports for all streams
- Analyze error patterns and frequencies
- Support for both master and media playlists

### 4. Database Operations (`update_db.py`)

Manage database operations for HLS monitoring data.

#### Usage:
```bash
python update_db.py
```

#### Features:
- Database connectivity and management
- SCTE-35 data population
- Alert management and processing

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific module tests
python -m pytest tests/test_monitor_captions.py -v
python -m pytest tests/test_add_remove.py -v
```

Test coverage includes:
- Stream management operations
- SSE connection handling
- Caption event processing
- Error conditions and edge cases
- Signal handling
- Command-line argument parsing

## Configuration

Settings can be modified in `config.py`:

```python
# API Configuration
SERVER_URL = os.environ.get('HLSANALYZER_SERVER', "https://hlsanalyzer.com")
API_KEY = os.environ.get('HLSANALYZER_APIKEY')

# SSE Configuration
SSE_TIMEOUT = 30                # SSE connection timeout
SSE_RECONNECT_DELAY = 5         # Delay between reconnection attempts
DEFAULT_MONITOR_DURATION = 60   # Default monitoring duration

# Database Configuration
INTERVAL_MINUTES = 400          # Update interval for database operations
```

## Error Handling

All scripts include comprehensive error handling for:

- **Missing API Key**: Clear error messages with setup instructions
- **Invalid Stream URLs**: API error responses from HLSAnalyzer
- **Network Issues**: Connection timeouts and retry logic
- **Authentication Errors**: Invalid API key detection
- **Service Unavailability**: Graceful handling of service downtime

## Troubleshooting

### Common Issues

1. **"HLSANALYZER_APIKEY environment variable is not set"**
   ```bash
   export HLSANALYZER_APIKEY="your-api-key-here"
   ```

2. **"Failed to add stream"**
   - Check stream URL format and accessibility
   - Verify API key is valid
   - Ensure proper network connectivity

3. **"Failed to connect to SSE endpoint"** (caption monitoring)
   - Check network connectivity
   - Verify server URL configuration
   - Confirm stream was added successfully

4. **No caption data received**
   - Verify stream contains 608 captions
   - Wait a few seconds for caption detection
   - Check stream is not in commercial break

5. **Permission/Import errors**
   - Ensure Python dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.7+)

### Getting Help

- **API Documentation**: [https://hlsanalyzer.com/api/documentation](https://hlsanalyzer.com/api/documentation)
- **Support**: Contact HLSAnalyzer support for API key issues
- **Issues**: Report bugs via the repository issue tracker

## License

MIT License - see individual files for full license text.
