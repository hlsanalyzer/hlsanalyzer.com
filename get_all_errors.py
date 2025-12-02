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
import utils
import os
from config import Config


def process_link_status(link_status):
    error_count = link_status['Errors']
    warning_count = link_status['Warnings']
    timestamp = link_status['Timestamp']
    linkid = link_status['LinkID']

    return (error_count, warning_count, timestamp, linkid)


def get_all_errors():

    server = Config.get_server_url()
    apikey = Config.API_KEY
    if not apikey:
        print("Error: HLSANALYZER_APIKEY environment variable is not set.")
        return

    print("="*60)
    print("HLSAnalyzer Error and Warning Report")
    print("="*60)

    #Get the status for all the links
    result = utils.get_all_status(server, apikey)

    if result is not None:
        total_streams = 0
        total_errors = 0
        total_warnings = 0
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
            total_streams += 1
            total_errors += int(float(error_count))
            total_warnings += int(float(warning_count))
            
            # Display error count and details
            if int(float(error_count)) > 0:
                print(f"    🚨 {error_count} Error(s) - LinkID: {linkid}")
                error_data = utils.get_records(server, apikey, linkid, 0, timestamp, mode="stream/errors")
                if error_data and 'errors' in error_data:
                    for error in error_data['errors']:
                        print(f"        ❌ {error.get('message', 'Unknown error')}")
                        if 'timestamp' in error:
                            print(f"           Time: {error['timestamp']}")
            
            # Display warning count and details  
            if int(float(warning_count)) > 0:
                print(f"    ⚠️  {warning_count} Warning(s) - LinkID: {linkid}")
                warning_data = utils.get_records(server, apikey, linkid, 0, timestamp, mode="stream/warnings")
                if warning_data and 'warnings' in warning_data:
                    for warning in warning_data['warnings']:
                        print(f"        ⚠️  {warning.get('message', 'Unknown warning')}")
                        if 'timestamp' in warning:
                            print(f"           Time: {warning['timestamp']}")
            
            # Show status if no errors or warnings
            if int(float(error_count)) == 0 and int(float(warning_count)) == 0:
                print(f"    ✅ No errors or warnings - LinkID: {linkid}")

            if has_variants:
                variant_status = result['status'][hls_link]['Variants']
                for variant in variant_status.keys():
                    print("|-- Variant [%s] "%(variant))
                    (error_count, warning_count, timestamp, linkid) = process_link_status(variant_status[variant])
                    total_streams += 1
                    total_errors += int(float(error_count))
                    total_warnings += int(float(warning_count))
                    
                    # Display variant error details
                    if float(error_count) > 0:
                        print(f"    🚨 {error_count} Error(s) - LinkID: {linkid}")
                        error_data = utils.get_records(server, apikey, linkid, 0, timestamp, "stream/errors")
                        if error_data and 'errors' in error_data:
                            for error in error_data['errors']:
                                print(f"        ❌ {error.get('message', 'Unknown error')}")
                                if 'timestamp' in error:
                                    print(f"           Time: {error['timestamp']}")
                    
                    # Display variant warning details
                    if float(warning_count) > 0:
                        print(f"    ⚠️  {warning_count} Warning(s) - LinkID: {linkid}")
                        warning_data = utils.get_records(server, apikey, linkid, 0, timestamp, "stream/warnings")
                        if warning_data and 'warnings' in warning_data:
                            for warning in warning_data['warnings']:
                                print(f"        ⚠️  {warning.get('message', 'Unknown warning')}")
                                if 'timestamp' in warning:
                                    print(f"           Time: {warning['timestamp']}")
                    
                    # Show variant status if no errors or warnings
                    if float(error_count) == 0 and float(warning_count) == 0:
                        print(f"    ✅ No errors or warnings - LinkID: {linkid}")

        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total streams monitored: {total_streams}")
        print(f"Total errors found: {total_errors}")
        print(f"Total warnings found: {total_warnings}")
        
        if total_errors == 0 and total_warnings == 0:
            print("🎉 All streams are healthy!")
        elif total_errors > 0:
            print("🚨 Issues found that require attention!")
        else:
            print("⚠️  Some warnings detected, monitoring recommended")
    else:
        print("❌ Failed to retrieve status information")


if __name__ == '__main__':
    get_all_errors()
