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
import utils
import os
from urllib.parse import urlencode


def add_remove_link():

    #Replace with actual endpoint and APIkey
    #For the primary server use "hlsanalyzer.com"
    server = "https://hlsanalyzer.com"
    apikey = os.environ.get('APIKEY')
    if not apikey:
        print("Error: APIKEY environment variable is not set.")
        return
    
    stream = "https://bitdash-a.akamaihd.net/content/sintel/hls/video/500kbit.m3u8"

    (code, result) = utils.send_command(server, apikey, "stream/add", ["m3u8=%s&linkid=STREAMTEST"%(stream)], method='POST')
    print(f"Adding stream = code = {code}, result = {result}")

    (code, result) = utils.send_command(server, apikey, "stream/remove", ["m3u8=%s"%(stream)], method='POST')
    print(f"Removing stream = code = {code}, result = {result}")
    

if __name__ == '__main__':
    add_remove_link()
