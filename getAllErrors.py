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


def process_link_status(link_status):
    error_count = link_status['Errors']
    warning_count = link_status['Warnings']
    timestamp = link_status['Timestamp']
    linkid = link_status['LinkID']

    return (error_count, warning_count, timestamp, linkid)


def get_all_errors():

    #Replace with endpoing and API Key
    server = "https://staging.hlsanalyzer.com"
    key = os.environ.get('APIKEY')

    #Get the status for all the links
    result = utils.get_all_status(server, key)

    if result is not None:
        #Traverse all HLS links being monitored.
        # Each link can be either a master playlist with variants, or a single Media playlist
        for hls_link in result['status'].keys():
            link_status = result['status'][hls_link]
            has_variants = False
            if 'Variants' in link_status:
                print("MASTER [%s]" %(hls_link))
                has_variants = True
            else:
                print("MEDIA [%s]" %(hls_link))

            (error_count, warning_count, timestamp, linkid) = process_link_status(link_status)
            if int(float(error_count)) > 0:
                utils.get_records(server, key, linkid, 0, timestamp, mode="stream/errors")
            if int(float(warning_count)) > 0:
                utils.get_records(server, key, linkid, 0, timestamp, mode="stream/warnings")

            if has_variants:
                variant_status = result['status'][hls_link]['Variants']
                for variant in variant_status.keys():
                    print("|-- Variant [%s] "%(variant))
                    (error_count, warning_count, timestamp, linkid) = process_link_status(variant_status[variant])
                    if float(error_count)> 0:
                        utils.get_records(server, key, linkid, 0, timestamp, "stream/errors")
                    if float(warning_count) > 0:
                        utils.get_records(server, key, linkid, 0, timestamp, "stream/warnings")


if __name__ == '__main__':
    get_all_errors()
