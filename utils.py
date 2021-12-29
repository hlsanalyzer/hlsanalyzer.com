#!/usr/local/bin/python3

# MIT License
# Copyright (c) 2021 HLSAnalyzer.com
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

def get_records(server, apikey, linkid, start, end, mode):

    try:
        url = "%s/api/%s?apikey=%s&start=%d&end=%d&linkid=%s" % (server, mode, apikey, start, end, linkid)
        response = load_from_uri(url, timeout=3)
        data = json.loads(response)
        return data

    except urllib.error.HTTPError as e:
        print("Error in checking status")
        print(e.code)
        print(e.read())
        return None
    except:
        print("Exception in reading records")
        return None


def load_from_uri(uri, timeout=3):
    request = Request(uri)
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
        response = load_from_uri(url, timeout=3)
        result_json = json.loads(response)
        return result_json
    except urllib.error.HTTPError as e:
        print("Error in adding link")
        print(e.code)
        print(e.read().decode())
        return None
    except:
        print("Exception in reading status")
        return None
