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

import urllib.request
import json
from urllib.request import Request, HTTPSHandler, build_opener, install_opener
import ssl
import os
from config import Config

def get_records(server, apikey, linkid, start, end, mode):

    try:
        url = "%s/api/%s?apikey=%s&start=%d&end=%d&linkid=%s" % (server, mode, apikey, start, end, linkid)
        response = load_from_uri(url)
        data = json.loads(response)
        return data

    except urllib.error.HTTPError as e:
        print("Error in checking status")
        print(e.code)
        print(e.read())
        return None
    except (json.JSONDecodeError, ValueError, ConnectionError) as e:
        print(f"Exception in reading records: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in reading records: {e}")
        return None

def send_command(server, apikey, command, params=None, method='GET'):
    try:
        url = "%s/api/%s?apikey=%s" % (server, command, apikey)
        if params is not None:
            for cur in params:
                url += "&%s" %(cur)

        print("URL = ", url)
        response= load_from_uri(url, method, timeout=Config.DEFAULT_TIMEOUT)
        responsej = json.loads(response)
        return (200, responsej)
    except urllib.error.HTTPError as e:
        response = e.read().decode()
        return (e.code, None)
    except (json.JSONDecodeError, ValueError, ConnectionError) as e:
        print(f"Exception in {command} command: {e}")
        return (500, None)
    except Exception as e:
        print(f"Unexpected error in {command} command: {e}")
        return (500, None)

def load_from_uri(uri, method = 'GET', timeout=Config.SEGMENT_DOWNLOAD_TIMEOUT):
    request = Request(uri, method=method)
    https_sslv3_handler = HTTPSHandler(context=ssl.SSLContext())
    opener = build_opener(https_sslv3_handler)
    install_opener(opener)
    resource = opener.open(request, timeout=timeout)

    content = _read_python3x(resource)
    return content


def _read_python3x(resource):
    final = None
    while True:
        cur = resource.read(1000)
        if (len(cur) == 0): break
        if final is None:
            final = ""
        final += cur.decode(resource.headers.get_content_charset(failobj="utf-8"))

    return final



def get_all_status(server, key):
    try:
        url = "%s/api/status?apikey=%s" % (server, key)
        response = load_from_uri(url)
        result_json = json.loads(response)
        return result_json
    except urllib.error.HTTPError as e:
        print("Error in adding link")
        print(e.code)
        print(e.read().decode())
        return None
    except (json.JSONDecodeError, ValueError, ConnectionError) as e:
        print(f"Exception in reading status: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in reading status: {e}")
        return None
