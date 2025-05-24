# coding=utf-8
import datetime
import time
import json
from faker import Faker
import re

# Load configuration
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

class Model1:

    def __init__(self, client, db):
        db_name = config['database']['name']
        db = client[db_name]  # Use the database name from the config file
        self.client = client
        self.db = db

    def data_generator(self, n):
        
        # 1. Collection Setup

        # Create 2 different collections
        collections = ['Person', 'Company']
        collection_objects = {}  # Dictionary to store collection objects

        # Drop existing collections except system collections
        for collection_name in self.db.list_collection_names():
            if not collection_name.startswith('system.'):
                self.db.drop_collection(collection_name)  # Drop existing collections except system collections
                print(f"Dropped collection: {collection_name}")

        for collection in collections:
            collection_objects[collection] = self.db.create_collection(collection)  # Create and obtain collection
        
        # 2. Data Generation

        fake = Faker(config['generation']['languages'])  # Create a Faker object with multiple languages
        
        person_company_ratio = config['generation']['person_company_ratio']  # Ratio of people to companies (with a default value)
        n_companies = n // person_company_ratio  # Number of companies to generate
        n_people = n - n_companies  # Number of people to generate
        
        # Generate companies first and keep track of their IDs
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
                "vatNumber": fake.uuid4(),
                "employeeIds": []  # Initialize empty array to store employee references (updated later)
            }
            
            company_domains[company_id] = c_domain
            company_ids.append(company_id)  # Store company ID for later use
            
            collection_objects['Company'].insert_one(c)  # Insert the generated data into the collection
        
        print(f"Generated {n_companies} companies with {len(company_ids)} unique IDs.")

        # Now generate people and assign each to a company
        companies_to_employees = {company_id: [] for company_id in company_ids}
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
                "sex": fake.random_element(elements=('M', 'F', 'O')),
                "companyId": assigned_company_id  # Reference to company
            }
            
            collection_objects['Person'].insert_one(p)  # Insert the generated data into the collection
            companies_to_employees[assigned_company_id].append(person_id)  # Track this person for the company's employee list
        
        print(f"Generated {n_people} people.")
        print(f"Total: {n} documents.")

        # Update each company with its employee references
        for company_id, employee_ids in companies_to_employees.items():
            collection_objects['Company'].update_one(
                {"_id": company_id},  # Filter document (company ID)
                {"$set": {"employeeIds": employee_ids}}  # Update the employeeIds field with the list of employee IDs
            )

        print("Updated all companies with employee references.")

        print("Data generation completed successfully.")

    def query_1(self):

        """For each person, retrieve full name and their company's name"""
    
        # Get the Person collection
        person_collection = self.db['Person']
        
        # Define the aggregation pipeline
        pipeline = [
            {
                "$lookup": {  # Look for the company names in the "Company" collection
                    "from": "Company",
                    "localField": "companyId",
                    "foreignField": "_id",
                    "as": "company"
                }
            },
            {
                "$unwind": "$company"  # Convert the array of companies into a single object 
            },
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
        
        # Get the Company collection
        company_collection = self.db['Company']
        
        # Define the aggregation pipeline
        pipeline = [
            {
                "$project": {  # Choose only certain attributes
                    "companyName": "$name",
                    "numEmployees": {"$size": "$employeeIds"}
                }
            }
        ]
        
        # Execute the aggregation query
        start_time = time.time()
        results = list(company_collection.aggregate(pipeline))
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

        # Get the Company collection
        company_collection = self.db['Company']

        # Execute the update query
        start_time = time.time()
        results = company_collection.update_many(
            filter = {},  # No filter, update all companies
            update = {"$set": {"name": "Company"}}
        )
        query_time = time.time() - start_time
        
        # Display the number of documents updated
        print("\n", "--" * 30)
        print(f"\nQuery 4 executed in {query_time} seconds.")
        print(f"Matched {results.matched_count} companies and updated {results.modified_count} companies to have the name 'Company'.")

        return query_time