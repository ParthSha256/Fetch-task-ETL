# importing libraries to use in the script

import boto3  # Importing boto3 library to interact with AWS
import json  # Importing json to modulate the json data
import hashlib  # Importing hashlib for masking PII
import psycopg2  # Importing psycopg2 for connecting and communicating with postgres database
from datetime import date

class Fetch_ETL:
    def __init__(self):
        # Configuration of AWS,SQS and PostgresSQL
        self.queue_url = "http://localhost:4566/000000000000/login-queue"
        self.DATABASE_CONFIG = {
            "database": "postgres",
            "user": "postgres",
            "password": "postgres",
            "host": "localhost",
            "port": 5432,  # Any random port can be chosen of choice but the image of postgres in compose
                           # should be hosted on that random port of choice.
        }

    def get_sqs_client(self):
        # Get the client of AWS SQS
        sqs = boto3.client('sqs', endpoint_url=self.queue_url)
        return sqs

    def read_from_sqs(self):
        # Read message from SQS
        sqs = self.get_sqs_client()
        messages = sqs.receive_message(QueueUrl=self.queue_url)
        return messages

    def mask_pii(self, field):
        # Masking method to mask PII
        masked_string = hashlib.sha256(field.encode()).hexdigest()
        return masked_string

    def convert_to_integer(self,version):
        version_number = version  # let version_number = 2.0.3
        components = version_number.split(".")  # ["2", "0", "3"]
        int_components = [int(component) for component in components]
        padded_int_components = [str(component).zfill(3) for component in int_components]  # ["002" , "000" , "003"]
        result_integer = int("".join(padded_int_components)) # [2000003]
        return result_integer

    def new_data(self, fresh_data):
        # Creating updated data with masked PII
        fresh_data['ip'] = self.mask_pii(fresh_data['ip'])
        fresh_data['device_id'] = self.mask_pii(fresh_data['device_id'])
        fresh_data['app_version'] = self.convert_to_integer(fresh_data['app_version'])
        return fresh_data

    def connect_to_postgres(self):
        # Connecting to postgres SQL
        connection = psycopg2.connect(user=self.DATABASE_CONFIG.get('user'),
                                      password=self.DATABASE_CONFIG.get('password'),
                                      host=self.DATABASE_CONFIG.get('host'),
                                      port=self.DATABASE_CONFIG.get('port'),
                                      database=self.DATABASE_CONFIG.get('database'))
        return connection

    def insert_data_to_postgres(self, cleaned_data):
        # Method to populate data in the created table "user_logins" from SQS
        connection = self.connect_to_postgres()
        cursor = connection.cursor()
        print(cleaned_data)
        today = date.today()
        insert_query = f"""
        INSERT INTO user_logins(
            user_id,
            device_type,
            masked_ip,
            masked_device_id,
            locale,
            app_version,
            create_date
        ) Values (
            '{cleaned_data['user_id']}',
            '{cleaned_data['device_type']}',
            '{cleaned_data['ip']}',
            '{cleaned_data['device_id']}',
            '{cleaned_data['locale']}',
            '{cleaned_data['app_version']}',
            '{today}'
               
        );
        """
        cursor.execute(insert_query)
        connection.commit()
        cursor.close()
        connection.close()

    def run_fetch_etl(self):
        # Processing messages from SQS
        while True:
            messages = self.read_from_sqs()

            # Handle the case when "messages" is None or "Messages" key is missing
            if messages is not None and "Messages" in messages:
                for i in messages["Messages"]:
                    body = json.loads(i["Body"])

                    # Check if the message has expected keys (To handle edge cases of unexpected data and to avoid
                    # breaking the loop in between because of bad data.)
                    if list(body.keys()) == ['user_id', 'app_version', 'device_type', 'ip', 'locale', 'device_id']:

                        curated_body = body
                        masked = self.new_data(curated_body)

                        # inserting data to postgres database hosted on docker
                        self.insert_data_to_postgres(masked)
            else:
                break


if __name__ == "__main__":
    ETL_Fetch_Task = Fetch_ETL()
    ETL_Fetch_Task.run_fetch_etl()
