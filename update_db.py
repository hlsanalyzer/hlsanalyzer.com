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
import mysql.connector
from mysql.connector import errorcode
import utils
import time
import hashlib
import re
from config import Config

INTERVAL_MINUTES = Config.INTERVAL_MINUTES
DBHOST = Config.DB_HOST
DBUSER = Config.DB_USER
DBPW = Config.DB_PASSWORD

def create_database(cursor, db_name):
    # Validate database name to prevent SQL injection
    import re
    if not re.match(r'^[a-zA-Z0-9_]+$', db_name):
        raise ValueError(f"Invalid database name: {db_name}. Only alphanumeric characters and underscores allowed.")
    
    if len(db_name) > Config.MAX_DB_NAME_LENGTH:
        raise ValueError(f"Database name too long: {db_name}. Maximum 64 characters allowed.")
    
    try:
        cursor.execute(
            "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(db_name))
    except mysql.connector.Error as err:
        print("Failed creating database: {}".format(err))
        raise


def connect_db():


    try:
        connection = mysql.connector.connect(user=DBUSER, password=DBPW,
                                      host=DBHOST)
        return connection
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error connecting to database: {e}")
        return None

def define_tables():
    TABLES = {}
    TABLES['AlertRecord']  = "CREATE TABLE AlertRecord (Timestamp INT, CreateTime INT, MasterID VARCHAR(32), VariantID VARCHAR(32), "\
                              "RecordHash VARCHAR(8), Record VARCHAR(255), PRIMARY KEY(Timestamp, VariantID, RecordHash))"
    TABLES['AlertSummary'] = "CREATE TABLE AlertSummary (Timestamp INT, CreateTime INT, MasterID VARCHAR(32), VariantID VARCHAR(32), "\
                              "RecordHash VARCHAR(8), Type VARCHAR(32), Status VARCHAR(32), Duration DOUBLE, Units VARCHAR(12), PRIMARY KEY(Timestamp, VariantID, RecordHash))"

    TABLES['SCTE35Record']  = "CREATE TABLE SCTE35Record (Timestamp INT, CreateTime INT, MasterID VARCHAR(32), VariantID VARCHAR(32), "\
                             "RecordHash VARCHAR(8), Record VARCHAR(255), PRIMARY KEY(Timestamp, VariantID, RecordHash))"
    TABLES['SCTE35Summary'] = "CREATE TABLE SCTE35Summary (Timestamp INT, CreateTime INT, MasterID VARCHAR(32), VariantID VARCHAR(32), "\
                             "RecordHash VARCHAR(8), Duration DOUBLE, PRIMARY KEY(Timestamp, VariantID, RecordHash))"

    return TABLES

def populate_scte35(db, cursor, records, master_id, link_id, create_time):
    if records is None:
        print("No records found for: %s, %s" %(master_id, link_id))
        return

    val_summary = []
    val_record = []

    for cur in records:
        ts = cur['timestamp']
        record = cur["scte35"]
        record_hash = hashlib.sha1(record.encode("UTF-8")).hexdigest()
        record_hash = record_hash[0:8]


        val_record.append ((ts, create_time, master_id, link_id, record_hash, record))

        m = re.search("Cue In (\d+.\d+) seconds", record)
        if (m):
            duration = m.group(1)
            val_summary.append((ts, create_time, master_id, link_id, record_hash, duration))

    if len(val_record) > 0:
        sql = """INSERT INTO SCTE35Record (Timestamp, CreateTime, MasterID, VariantID, RecordHash, Record) VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE Timestamp=Timestamp,VariantID=VariantID,RecordHash=RecordHash"""

        try:
            cursor.executemany(sql, val_record)
        except mysql.connector.Error as err:
            print(err.msg)


    if len(val_summary) > 0:
        sql = """INSERT INTO SCTE35Summary (Timestamp, CreateTime, MasterID, VariantID, RecordHash, Duration) VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE Timestamp=Timestamp,VariantID=VariantID,RecordHash=RecordHash"""

        try:
            cursor.executemany(sql, val_summary)
        except mysql.connector.Error as err:
            print(err.msg)

    db.commit()


def populate_alerts(db, cursor, records, master_id, link_id, create_time):
    if records is None:
        print("No records found for: %s, %s" %(master_id, link_id))
        return

    val_summary = []
    val_record = []

    for cur in records:
        ts = cur['timestamp']
        record = cur["alerts"]
        record_hash = hashlib.sha1(record.encode("UTF-8")).hexdigest()
        record_hash = record_hash[0:8]


        val_record.append ((ts, create_time, master_id, link_id, record_hash, record))

        m = re.search("(SCTE-35|STREAM) (OUTAGE ALERT|ALERT CLEARED) .* (\d+) (minutes|seconds)", record)
        if (m):
            type=m.group(1)
            status=m.group(2)
            duration = m.group(3)
            units=m.group(4)
            val_summary.append((ts, create_time, master_id, link_id, record_hash, type, status, duration, units))

    if len(val_record) > 0:
        sql = """INSERT INTO AlertRecord (Timestamp, CreateTime, MasterID, VariantID, RecordHash, Record) VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE Timestamp=Timestamp,VariantID=VariantID,RecordHash=RecordHash"""

        try:
            cursor.executemany(sql, val_record)
        except mysql.connector.Error as err:
            print(err.msg)


    if len(val_summary) > 0:
        sql = """INSERT INTO AlertSummary (Timestamp, CreateTime, MasterID, VariantID, RecordHash, Type, Status, Duration, Units) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE Timestamp=Timestamp,VariantID=VariantID,RecordHash=RecordHash"""

        try:
            cursor.executemany(sql, val_summary)
        except mysql.connector.Error as err:
            print(err.msg)

    db.commit()


def update_hlsanalyzer_content(apikey, apihost):

    db = connect_db()
    if db is None:
        raise Exception("Could not connect to database!")
    else:
        print("Connected.")

    cursor = db.cursor()


    if apikey is None:
        raise Exception("API Key not found!")
    
    # Validate API key format
    import re
    if not re.match(r'^[a-zA-Z0-9\-]+$', apikey):
        raise ValueError(f"Invalid API key format: contains invalid characters")
    
    db_name = apikey.replace("-","")
    
    # Validate resulting database name
    if not re.match(r'^[a-zA-Z0-9_]+$', db_name):
        raise ValueError(f"API key generates invalid database name: {db_name}")
    
    if len(db_name) > Config.MAX_DB_NAME_LENGTH:
        raise ValueError(f"API key generates database name too long: {db_name}")

    try:
        cursor.execute("USE {}".format(db_name))
    except mysql.connector.Error as err:
        print("Database {} does not exists.".format(db_name))
        if err.errno == errorcode.ER_BAD_DB_ERROR:
            create_database(cursor, db_name)
            print("Database {} created successfully.".format(db_name))
            db.database = db_name
        else:
            print(err)

    TABLES = define_tables()

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print("Creating table {}: ".format(table_name), end='')
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)
        else:
            print("OK")

    create_time = int(time.time())
    duration = INTERVAL_MINUTES*60
    result = utils.get_all_status(apihost, apikey)

    if result is not None:
        #Traverse all HLS links being monitored.
        # Each link can be either a master playlist with variants, or a single Media playlist
        variant_list = []
        for hls_link in result['status'].keys():
            link_status = result['status'][hls_link]
            has_variants = False
            timestamp = link_status["Timestamp"]
            cur_id = link_status["LinkID"]

            if 'Variants' in link_status:
                print("MASTER [%s]" %(hls_link))
                master_id = cur_id
                variant_status = result['status'][hls_link]['Variants']
                for variant in variant_status.keys():
                    print("|-- Variant [%s] "%(variant))
                    variant_id = variant_status[variant]["LinkID"]
                    variant_list.append( (master_id, variant_id, timestamp))
            else:
                print("SINGLE MEDIA [%s]" %(hls_link))
                variant_list.append((None, cur_id, timestamp))

        for (master_id, cur_id, timestamp) in variant_list:
            records = utils.get_records(apihost, apikey, cur_id, timestamp - duration, timestamp, mode="stream/scte35cues")
            populate_scte35(db, cursor, records, master_id, cur_id, create_time)
            records = utils.get_records(apihost, apikey, cur_id, timestamp - duration, timestamp, mode="stream/alertevents")
            populate_alerts(db, cursor, records, master_id, cur_id, create_time)


    print("Finished processing database ", db_name)
    cursor.close()
    db.close()

if __name__ == '__main__':
    apikey = Config.API_KEY
    apihost = Config.get_server_url()
    update_hlsanalyzer_content(apikey, apihost)