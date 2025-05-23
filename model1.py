# coding=utf-8
import datetime
import time
import json
from pymongo import MongoClient
from faker import Faker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

class Model1:
    def data_generator(self, n):

        # 1. Database Setup

        # Connect to MongoDB from environment variable - Note: Change connection string as needed
        client = MongoClient(os.getenv('MONGO_PORT'))
        # Connect to the database (creates it lazily if it doesn't exist) - will 
        # be actually created when the first document is insereted into a collection
        db_name = config['database']['name']
        db = client[db_name]  # Use the database name from the config file
        
        # 2. Collection Setup

        # Create 2 different collections
        collections = ['Person', 'Company']
        collection_objects = {}  # Dictionary to store collection objects

        for collection in collections:
            db.drop_collection(collection)  # Delete collection data if exists
            collection_objects[collection] = db.create_collection(collection)  # Create and obtain collection
        
        # 3. Data Generation

        fake = Faker(config['generation']['languages'])  # Create a Faker object with multiple languages
        
        person_company_ratio = config['generation']['person_company_ratio']  # Ratio of people to companies (with a default value)
        n_companies = n // person_company_ratio  # Number of companies to generate
        n_people = n - n_companies  # Number of people to generate
        
        # Generate companies first and keep track of their IDs
        company_ids = []
        for x in range(n_companies):  # Generate n_companies documents
            
            # Generate random data with consistency
            c_name = fake.company()
            c_email = "@" + c_name.replace(" ", "").lower() + ".com"
            c_url = c_name.replace(" ", "").lower() + ".com"
            
            # Create custom company IDs (not MongoDB default ObjectId)
            company_id = fake.company_business_id()
            
            c = {
                "_id": company_id,
                "domain": fake.company_category(),
                "email": c_email,
                "name": c_name, 
                "url": c_url, 
                "vatNumber": fake.company_vat(),
                "employeeIds": []  # Initialize empty array to store employee references (updated later)
            }
            
            company_ids.append(company_id)  # Store company ID for later use
            
            collection_objects['Company'].insert_one(c)  # Insert the generated data into the collection
            print(str(x+1) + ". Company document inserted")
        
        # Now generate people and assign each to a company
        companies_to_employees = {company_id: [] for company_id in company_ids}
        for x in range(n_people):  # Generate n_people documents
            
            # Generate random data with consistency
            date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80)
            age = datetime.datetime.now().year - date_of_birth.year
            first_name = fake.first_name()
            last_name = fake.last_name()
            full_name = first_name + " " + last_name
            
            # Assign person to a random company
            assigned_company_id = fake.random_element(elements=company_ids)
            
            person_id = fake.identity_card_number()
            
            p = {
                "_id": person_id,
                "age": age,
                "companyEmail": fake.company_email(),
                "dateOfBirth": date_of_birth,
                "email": fake.email(),
                "firstName": first_name,
                "fullName": full_name,
                "sex": fake.random_element(elements=('M', 'F', 'O')),
                "companyId": assigned_company_id  # Reference to company
            }
            
            collection_objects['Person'].insert_one(p)  # Insert the generated data into the collection
            companies_to_employees[assigned_company_id].append(person_id)  # Track this person for the company's employee list
            print(str(x+1) + ". Person document inserted")
        
        # Update each company with its employee references
        for company_id, employee_ids in companies_to_employees.items():
            collection_objects['Company'].update_one(
                {"_id": company_id},  # Filter document (company ID)
                {"$set": {"employeeIds": employee_ids}}  # Update the employeeIds field with the list of employee IDs
            )
            print(f"Updated company {company_id} with {len(employee_ids)} employee references")
        
        # 4. Performance Testing

        # Get time at the start of the query
        start_time = time.time()  # Measure the time before running the query
        result = collection_objects['Person'].find_one()  # Retrieve one document from the collection
        query_time = time.time() - start_time  # Measure the time taken to execute the query
        # Display the query execution time and the result
        print("--- %s seconds ---" % (query_time) + str(result))
        
        # 5. Close the connection

        client.close()