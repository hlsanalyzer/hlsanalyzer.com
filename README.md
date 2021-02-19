# HLSAnalyzer.com API Sample Code
HLSAnalyzer.com is a service that allows continuous monitoring of live HLS streams. The monitoring service is performed using a dedicated real-time monitoring instance, along with a browser-based interface for reviewing stream status and examining various aspects of HLS validation.  HLSAnalyzer downloads all segments and playlists for each HLS variant. Master playlists are downloaded every 30 seconds and processed for media playlist changes. Alerts are configurable to report slow delivery of streams (or complete outages) as well as the recovery time, via email and HTTP POSTs. 

The monitoring service has a browser-based interface along with an HTTP-based API which enables programmatic interaction with the monitoring instance. This repository provides examples of how to interact with the API.  The complete API documentation can be found here: [https://hlsanalyzer.com/api/documentation](https://hlsanalyzer.com/api/documentation)

This repository contains sample code for interacting with the HLSAnalyzer HTTP API.
