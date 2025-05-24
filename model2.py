# coding=utf-8
import datetime
import time
import json
from pymongo import MongoClient
from faker import Faker
import re

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

class Model2:

    def __init__(self, client, db):
        self.client = client
        self.db = db

    def data_generator(self, n):
        
        # 1. Collection Setup

        # Create only one collection
        for collection_name in self.db.list_collection_names():
            if not collection_name.startswith('system.'):
                self.db.drop_collection(collection_name)  # Drop existing collections except system collections
                print(f"Dropped collection: {collection_name}")

        # Create only the Person collection
        collection_objects = {'Person': self.db.create_collection('Person')}
        
        # 2. Data Generation

        fake = Faker(config['generation']['languages'])  # Create a Faker object with multiple languages
        
        person_company_ratio = config['generation']['person_company_ratio']  # Ratio of people to companies (with a default value)
        n_companies = n // person_company_ratio  # Number of companies to generate
        n_people = n - n_companies  # Number of people to generate
        
        # Generate companies first and keep track of their IDs
        company_list = []  # List to store company data for later use
        company_ids = []
        company_domains = {}  # Dictionary to store company domains for later use
        for x in range(n_companies):  # Generate n_companies documents
            
            # Generate random data with consistency
            c_name = fake.company()
            c_domain = "@" + re.sub(r'[^\w]', '', c_name).lower() + ".com"
            c_email = 'customers' + c_domain
            c_url = c_name.replace(" ", "").lower() + ".com"
            
            # Create custom company IDs (not MongoDB default ObjectId)
            company_id = fake.uuid4()
            
            c = {
                "_id": company_id,
                "domain": c_domain,
                "email": c_email,
                "name": c_name, 
                "url": c_url, 
                "vatNumber": fake.uuid4()
            }
            
            company_list.append(c)  # Store the company data
            company_domains[company_id] = c_domain
            company_ids.append(company_id)  # Store company ID for later use
                    
        print(f"Generated {n_companies} companies with {len(company_ids)} unique IDs.")

        # Now generate people and assign each to a company
        for x in range(n_people):  # Generate n_people documents
            
            # Generate random data with consistency
            person_id = fake.uuid4()
            date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=80)
            date_of_birth_dt = datetime.datetime.combine(date_of_birth, datetime.time.min)  # Convert date_of_birth to datetime.datetime object to ensure compatibility with MongoDB
            age = datetime.datetime.now().year - date_of_birth.year
            first_name = fake.first_name()
            last_name = fake.last_name()
            full_name = first_name + " " + last_name
            email = first_name.lower() + '.' + last_name.lower() + '@' + 'example.com'
            
            # Assign person to a random company
            assigned_company_id = fake.random_element(elements=company_ids)
            company_domain = company_domains[assigned_company_id]

			# Create custom company email from the company name
            company_email = first_name.lower() + '.' + last_name.lower() + company_domain
            
            p = {
                "_id": person_id,
                "age": age,
                "companyEmail": company_email,
                "dateOfBirth": date_of_birth_dt,
                "email": email,
                "firstName": first_name,
                "fullName": full_name,
                "sex": fake.random_element(elements=('M', 'F', 'O'))
            }

            # Append the company dictionary corresponding to the assigned company ID
            # to the person dictionary
            company = next((c for c in company_list if c['_id'] == assigned_company_id), None)
            p["company"] = company
            
            collection_objects['Person'].insert_one(p)  # Insert the generated data into the collection
        
        print(f"Generated {n_people} people.")
        print(f"Total: {n_people} documents.")
        print("Data generation completed successfully.")

    def query_1(self):

        """For each person, retrieve full name and their company's name"""
    
        # Get the Person collection
        person_collection = self.db['Person']
        
        # Define the aggregation pipeline
        pipeline = [
            {
                "$project": {  # Choose only certain attributes
                    "fullName": "$fullName",
                    "companyName": "$company.name"  # Get only the company name
                }
            }
        ]
        
        # Execute the aggregation query
        start_time = time.time()
        results = list(person_collection.aggregate(pipeline))
        query_time = time.time() - start_time

        # Display length of results
        print("\n", "--" * 30)
        print(f"\nQuery 1 executed in {query_time} seconds.")
        print(f"Found {len(results)} people with their companies. First 5 results:")
        
        for result in results[:5]:  # Display only the first 5 results
            print(f"- {result['fullName']} works at {result['companyName']}")
        
        return query_time
    
    def query_2(self):

        """For each company, retrieve its name and the number of employees"""
        
        # Get the Person collection (since companies are embedded in Person)
        person_collection = self.db['Person']
        
        # Define the aggregation pipeline
        pipeline = [
            {
                "$group": {
                    "_id": "$company._id",  # Group all Person documents by their company's ID, creating one result per unique company
                    "companyName": { "$first": "$company.name" },  # For each company group, take the company name from the first document in that group
                    "numEmployees": { "$sum": 1 }  # Counts one for each document in each group, giving us the total number of employees per company
                }
            }
        ]
        
        # Execute the aggregation query
        start_time = time.time()
        results = list(person_collection.aggregate(pipeline))
        query_time = time.time() - start_time

        # Display length of results
        print("\n", "--" * 30)
        print(f"\nQuery 2 executed in {query_time} seconds.")
        print(f"Found {len(results)} companies. First 5 results:")
        
        for result in results[:5]:  # Display only the first 5 results
            print(f"- {result['companyName']} has {result['numEmployees']} employees")
        
        return query_time

    def query_3(self):

        """For each person born before 1988, update their age to “30”"""

        # Get the Person collection
        person_collection = self.db['Person']
        
        # Execute the update query
        start_time = time.time()
        results = person_collection.update_many(
            filter = {
                "$expr": {  # Allows us to use aggregation expressions (like $year) in the query
                    "$lt": [{"$year": "$dateOfBirth"}, 1988]  # Compute year of birth and compare it
                }
            },
            update = {"$set": {"age": 30}}
        )
        query_time = time.time() - start_time
        
        # Display the number of documents updated
        print("\n", "--" * 30)
        print(f"\nQuery 3 executed in {query_time} seconds.")
        print(f"Matched {results.matched_count} people and updated {results.modified_count} people born before 1988 to have age 30.")

        return query_time

    def query_4(self):

        """For each company, update its name to include the word “Company”"""

        # Get the Person collection (since companies are embedded in Person)
        person_collection = self.db['Person']

        # Execute the update query
        start_time = time.time()
        results = person_collection.update_many(
            filter = {},  # No filter, update all companies
            update = {"$set": {"company.name": "Company"}}
        )
        query_time = time.time() - start_time
        
        # Display the number of documents updated
        print("\n", "--" * 30)
        print(f"\nQuery 4 executed in {query_time} seconds.")
        print(f"Matched {results.matched_count} documents and updated company names of {results.modified_count} documents to have the name 'Company'.")

        return query_time