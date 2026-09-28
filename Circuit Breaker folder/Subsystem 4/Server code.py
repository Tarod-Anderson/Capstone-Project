import boto3
import pyodbc
import os
import json
from datetime import datetime

#allows easily changing queues, regions, and download location
queue_url = "https://sqs.us-east-1.amazonaws.com/899427357429/Bucket_notifications"
region = "us-east-1"


format = "%Y-%m-%d %H:%M:%S"

sqs = boto3.client("sqs", region_name=region)
s3 = boto3.client("s3", region_name=region)

DOWNLOAD_DIR = r"C:\sqs-downloads"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
UPLOAD_DIR = r"C:\sqs-uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

print("listening")

while True:
    response = sqs.receive_message(
        QueueUrl=queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=20
    )

    if "Messages" not in response:
        continue
  
    for message in response["Messages"]:
        # basically read the message from the queue
        body = json.loads(message["Body"])
        s3_event = body
        record = s3_event["Records"][0]["s3"]
        bucket = record["bucket"]["name"]
        key = record["object"]["key"]

        filename = os.path.basename(key)
        destination_path = os.path.join(DOWNLOAD_DIR, filename)

        #download json
        print("Downloading...")
        s3.download_file(bucket, key, destination_path)
        print("Download complete")

        #open json
        with open(destination_path, 'r') as f:
            record = json.load(f)
            
            #extract data
            vestid = record["vestid"]
            encounterstart = record["encounterstart"]
            encounterend = record["encounterend"]
            start = datetime.strptime(encounterstart, format)
            end = datetime.strptime(encounterend, format)
            encounterduration = (end - start).total_seconds() #compute duration of encounter
            latitude = record["latitude"]
            longitude = record["longitude"]
            altitude = record["altitude"]
            closestdistance = record["closestdistance"]
            

            try:
                #connect to SQL server #FIXME
                conn = pyodbc.connect(
                    'DRIVER={ODBC Driver 17 for SQL Server};'
                    r'SERVER=localhost\SQLEXPRESS01;'
                    'DATABASE=master;'
                    'Trusted_Connection=yes;'
                )
                #allow to control the server
                cursor = conn.cursor()

                #insert data into SQL server
                cursor.execute("""
                        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'contacts')
                                        BEGIN
                                            CREATE TABLE contacts(
                                                vestid VARCHAR(50),
                                                encounterstart VARCHAR(50),
                                                encounterend VARCHAR(50),
                                                encounterduration VARCHAR(50),
                                                closestdistance VARCHAR(50),
                                                latitude varchar(50),
                                                longitude varchar(50),
                                                altitude varchar(50)
                                            );
                                        END;
                                INSERT INTO contacts (vestid, encounterstart, encounterend, encounterduration, closestdistance, latitude, longitude, altitude)
                                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                                """, vestid, encounterstart, encounterend, encounterduration, closestdistance, latitude, longitude, altitude)
                conn.commit()
                print("data inserted")

                #retreive data from table
                cursor.execute("SELECT * FROM contacts")
                rows = cursor.fetchall()
                columns = [column[0] for column in cursor.description]
                data = [dict(zip(columns, row)) for row in rows]    #this line right here is magic.
                

                
                #get number of contacts for use later
                numcontacts = len(rows)

                #find earliest time and latest time
                times = cursor.execute("SELECT encounterstart, encounterend FROM contacts")
                start_times = []
                end_times = []

                for time in times:
                    st, et = time
                    start_times.append(datetime.strptime(st, format))
                    end_times.append(datetime.strptime(et, format))
                earliest_time = min(start_times)
                latest_time = max(end_times)
                timespan = latest_time - earliest_time
                seconds = int(timespan.total_seconds())

                #convert timespan to hours, days, weeks
                numhours = seconds // 3600
                if (numhours == 0): numhours = 1 #converts 0 hours to 1 hour
                numdays = numhours // 24
                if (numdays == 0): numdays = 1 #converts 0 days to 1 day
                numweeks = numdays // 7
                if (numweeks == 0): numweeks = 1 #converts 0 weeks to 1 week

                contperhour = numcontacts // int(numhours)
                contperday = numcontacts // int(numdays)
                contperweek = numcontacts // int(numweeks)

                #frequency part of JSON
                frequency = {
                    "number of contacts per hour": contperhour,
                    "number of contacts per day": contperday,
                    "number of contacts per week": contperweek
                }

                output = {
                    "contacts": data,
                    "frequency": frequency
                }


                #package data as json file and send it back
                response_path = os.path.join(UPLOAD_DIR, "response")
                with open(response_path, 'w') as f:
                    json.dump(output, f, default=str)
                print("generated response JSON")

                #upload response json to s3
                s3.upload_file(
                    response_path,
                    bucket,
                    "responses/response"
                )
                print("uploaded response JSON")

                #close connection
                cursor.close()
                conn.close()
                
                try:
                    os.remove(destination_path)
                    os.remove(response_path)
                    print("local Jsons deleted")
                except Exception as e:
                    print("failed to delete local Jsons:", e)
            except Exception as e:
                print("Insrtion failed:", e)
                continue


        #delete sqs message
        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message["ReceiptHandle"]
        )
        print("Message deleted")
