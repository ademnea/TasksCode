#!/usr/bin/env python3

import datetime
import mysql.connector
import csv

def get_data():
    # Connect to the database
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='W1m3@-d6p@55',
        database='ademnea'
    )
    cur = conn.cursor()
    
    # Define start and end dates for the query
    start_date = datetime.datetime(2025, 1, 1)
    end_date = datetime.datetime(2025, 3, 31)
    
    # Execute SQL query with ORDER BY clause
    query = ("SELECT record, created_at FROM hive_humidity "
             "WHERE created_at >= %s AND created_at <= %s AND hive_id = 1 "
             "ORDER BY created_at ASC")  # Sorting in ascending order
    cur.execute(query, (start_date, end_date))
    data = cur.fetchall()
    
    # Close the cursor and connection
    cur.close()
    conn.close()
    
    return data

def save_data(data):
    # Save data to CSV file
    with open('/var/www/html/ademnea_website/MODULES/csv_data/hive_humidity_hive1.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(['record', 'created_at'])
        for row in data:
            writer.writerow(row)

if __name__ == '__main__':
    data = get_data()
    save_data(data)
