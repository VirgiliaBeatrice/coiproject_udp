#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import sqlite3 as sql


DB_NAME = u"test.db"


def is_file_existed():
    print os.path.exists(DB_NAME)


def connect_database():
    if os.path.exists(DB_NAME):
        conn = sql.connect(DB_NAME)
        print(u"Opened database successfully.\r\n")
    else:
        conn = sql.connect(DB_NAME)
        print(u"Created database successfully.\r\n")

    return conn


def create_table(conn):
    # conn = sql.connect(DB_NAME)
    conn.execute(u'''CREATE TABLE SENSOR_DATA
        (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        DEV_ID TEXT NOT NULL,
        RAW_DATA TEXT NOT NULL,
        PROCESSED_DATA TEXT NOT NULL,
        TIMESTAMP DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')


is_file_existed()
conn = connect_database()
create_table(conn)
