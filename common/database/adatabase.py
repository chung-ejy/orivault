from pymongo import MongoClient, DESCENDING
import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
import certifi
ca = certifi.where()

# Purpose: This class provides functionality for managing MongoDB connections, storing, retrieving, 
# querying, and processing data, either locally or in the cloud.
class ADatabase(object):
    
    # Purpose: Initializes the database instance with a given name and retrieves the MongoDB token 
    # from environment variables.
    def __init__(self, name):
        self.name = name
        self.token = os.getenv("MONGOKEY")
        
    # Purpose: Establishes a connection to the local MongoDB instance running on localhost at port 27017.
    def connect(self):
        self.client = MongoClient("localhost", 27017)
    
    # Purpose: Establishes a secure connection to the MongoDB Atlas cloud database using the provided token and certificate.
    def cloud_connect(self):
        self.client = MongoClient(self.token, tlsCAFile=ca)
    
    # Purpose: Closes the connection to the MongoDB client to release resources.
    def disconnect(self):
        self.client.close()

    # Purpose: Stores data in the specified table within the database.
    # Inputs:
    # - table_name (str): Name of the table to store data.
    # - data (DataFrame): Pandas DataFrame containing the records to be inserted.
    def store(self, table_name, data):
        try:
            db = self.client[self.name]
            table = db[table_name]
            records = data.to_dict("records")
            table.insert_many(records)
        except Exception as e:
            print(self.name, table_name, str(e))
    
    # Purpose: Retrieves all records from the specified table, excluding the "_id" field.
    # Inputs:
    # - table_name (str): Name of the table to retrieve data from.
    # Returns:
    # - Pandas DataFrame containing the retrieved records.
    def retrieve(self, table_name):
        try:
            db = self.client[self.name]
            table = db[table_name]
            data = table.find({}, {"_id": 0}, show_record_id=False)
            return pd.DataFrame(list(data))
        except Exception as e:
            print(self.name, table_name, str(e))
    
    # Purpose: Retrieves records from the specified table based on a provided query.
    # Inputs:
    # - table_name (str): Name of the table to query data from.
    # - query (dict): MongoDB query dictionary to filter records.
    # Returns:
    # - Pandas DataFrame containing the queried records.
    def query(self, table_name, query):
        try:
            db = self.client[self.name]
            table = db[table_name]
            data = table.find(query, {"_id": 0}, show_record_id=False)
            return pd.DataFrame(list(data))
        except Exception as e:
            print(self.name, table_name, str(e))
    
    # Purpose: Creates a descending index on a specified column in the table.
    # Inputs:
    # - table_name (str): Name of the table to create an index in.
    # - col (str): Name of the column to index.
    def create_index(self, table_name, col):
        try:
            db = self.client[self.name]
            table = db[table_name]
            table.create_index([(col, DESCENDING)], unique=False)
        except Exception as e:
            print(self.name, table_name, str(e))
    
    # Purpose: Drops the specified table from the database, permanently removing its contents.
    # Inputs:
    # - table_name (str): Name of the table to be dropped.
    def drop(self, table_name):
        try:
            db = self.client[self.name]
            table = db[table_name]
            table.drop()
        except Exception as e:
            print(self.name, table_name, str(e))