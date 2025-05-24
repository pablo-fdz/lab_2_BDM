# coding=utf-8
from model1 import Model1
from model2 import Model2
from model3 import Model3
import json
import sys
from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Load configuration file
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

# Show options for the user when the program starts
def show_options():
    print("Choose the option you want to execute:")
    print("\t 0 - Exit")
    print("\t 1 - Model 1")
    print("\t 2 - Model 2")
    print("\t 3 - Model 3")

show_options()
op = int(input())

# Connect to MongoDB from environment variable - Note: Change connection string as needed
client = MongoClient(os.getenv('MONGO_PORT'))

# Connect to the database (creates it lazily if it doesn't exist) - will 
# be actually created when the first document is insereted into a collection
db_name = config['database']['name']

db = client[db_name]  # Use the database name from the config file

while op != 0:
    if op == 1:
        n = int(input("Insert the number of documents to create:"))
        m = Model1(client=client, db=db)
        m.data_generator(n)
        q = int(input("\nExecute queries? (1 for Yes, 0 for No): "))
        if q == 1:
            print("Executing queries...")
            time_q1 = m.query_1()
            time_q2 = m.query_2()
            time_q3 = m.query_3()
            time_q4 = m.query_4()
            print("\n", "==" * 10, "MODEL 1 RESULTS", "==" * 10, "\n")
            print("Query 1 time: ", time_q1)
            print("Query 2 time: ", time_q2)
            print("Query 3 time: ", time_q3)
            print("Query 4 time: ", time_q4)
            print("\n", "==" * 8, "END OF MODEL 1 RESULTS", "==" * 8, "\n")
        elif q == 0:
            print("Skipping query execution.")
        else:
            print("Invalid input. Please enter 1 for Yes or 0 for No.")
            sys.exit()
    elif op == 2:
        n = int(input("Insert the number of documents to create:"))
        m = Model2(client=client, db=db)
        m.data_generator(n)
        q = int(input("\nExecute queries? (1 for Yes, 0 for No): "))
        if q == 1:
            print("Executing queries...")
            time_q1 = m.query_1()
            time_q2 = m.query_2()
            time_q3 = m.query_3()
            time_q4 = m.query_4()
            print("\n", "==" * 10, "MODEL 2 RESULTS", "==" * 10, "\n")
            print("Query 1 time: ", time_q1)
            print("Query 2 time: ", time_q2)
            print("Query 3 time: ", time_q3)
            print("Query 4 time: ", time_q4)
            print("\n", "==" * 8, "END OF MODEL 2 RESULTS", "==" * 8, "\n")
        elif q == 0:
            print("Skipping query execution.")
        else:
            print("Invalid input. Please enter 1 for Yes or 0 for No.")
            sys.exit()
    elif op == 3:
        n = int(input("Insert the number of documents to create:"))
        m = Model3(client=client, db=db)
        m.data_generator(n)
        q = int(input("\nExecute queries? (1 for Yes, 0 for No): "))
        if q == 1:
            print("Executing queries...")
            time_q1 = m.query_1()
            time_q2 = m.query_2()
            time_q3 = m.query_3()
            time_q4 = m.query_4()
            print("\n", "==" * 10, "MODEL 3 RESULTS", "==" * 10, "\n")
            print("Query 1 time: ", time_q1)
            print("Query 2 time: ", time_q2)
            print("Query 3 time: ", time_q3)
            print("Query 4 time: ", time_q4)
            print("\n", "==" * 8, "END OF MODEL 3 RESULTS", "==" * 8, "\n")
        elif q == 0:
            print("Skipping query execution.")
        else:
            print("Invalid input. Please enter 1 for Yes or 0 for No.")
            sys.exit()
    else:
        print ("Exitting and closing the client...")
        client.close()  # Close the connection to MongoDB
        sys.exit()

    # After each operation, show options again
    show_options()
    op = int(input())

# Final cleanup when the user selects option 0 to exit the program
print("Exitting and closing the client...")
client.close()  # Close the connection to MongoDB