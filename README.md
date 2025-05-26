# Lab 2 - Document Database Performance Comparison

This lab tests the performance of three different document database models in MongoDB with four standardized queries. The project compares different approaches to modeling relationships between people and companies in a NoSQL document database.

## Requirements: Software Dependencies

- **MongoDB Community Server** (v8.0.9 or later)
- **MongoDB Shell (mongosh)** (v2.5.1 or later)
- **Python 3.7+**
- **Python packages**:
  - `pymongo`
  - `faker`
  - `python-dotenv`

## Installation and Setup

### 1. MongoDB Installation
Download and install MongoDB Community Server and MongoDB Shell from the official MongoDB website.

### 2. Python Dependencies

Install directly through `pip`:

```bash
pip install pymongo faker python-dotenv
```

Install through the `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Project Setup

1. Clone or download the project files
2. Create the data directory structure within the folder of the repository:
```bash
mkdir -p data/db
```

3. Make shell scripts executable:
```bash
chmod +x start_mongo.sh stop_mongo.sh
```

## Configuration

### Environment Variables (`.env`)

In a `.env` file, set the port for the MongoDB connection (the default is shown below) using the following naming:

```properties
MONGO_PORT = '127.0.0.1:27017'  
```

### Configuration File (`config.json`)

The configuration file specifies the name of the created database, the proportion of people documents compared to company documents and the languages that `faker` uses to create the synthetic data.

```json
{
    "database": {
        "name": "bdm_lab2"
    },
    "generation": {
        "person_company_ratio": 50,
        "languages": ["it_IT", "en_US", "es_ES"]
    }
}
```

## How to Run

### 1. Start MongoDB Server
```bash
./start_mongo.sh
```
Or manually:
```bash
mongod --dbpath ./data/db
```

### 2. Run the Performance Tests
In a separate terminal: 

1. Activate the Python virtual environment containing the installed Python dependencies.

2. Run the modeling and querying Python script:

   ```bash
   python model_query_program.py
   ```

3. Follow the instructions displayed by the program (more information below).

### 3. Stop MongoDB Server

```bash
./stop_mongo.sh
```
Or press `Ctrl+C` in the MongoDB server terminal.

## Program Structure

The main program (`model_query_program.py`) provides an interactive menu to:
1. Select which model to test (1, 2, or 3)
2. Specify the number of documents to generate
3. Choose whether to execute performance queries
4. View timing results for each query

## Document Database Models

### Model 1: Normalized (Reference-based)
**Collections:** `Person`, `Company`

**Structure:**
- **Person Collection:** Contains person data with `companyId` reference
- **Company Collection:** Contains company data with `employeeIds` array of references

**Characteristics:**
- Similar to relational database normalization
- Requires `$lookup` operations for joins
- Minimal data duplication
- Good for write-heavy workloads

**Example Documents:**
```javascript
// Person document
{
    "_id": "person-uuid",
    "fullName": "John Doe",
    "age": 30,
    "companyId": "company-uuid",
    // ... other fields
}

// Company document
{
    "_id": "company-uuid", 
    "name": "Tech Corp",
    "employeeIds": ["person-uuid1", "person-uuid2"],
    // ... other fields
}
```

### Model 2: Denormalized (Embedded Company in Person)
**Collections:** `Person` only

**Structure:**
- **Person Collection:** Contains person data with complete company object embedded

**Characteristics:**
- Company data duplicated across multiple person documents
- No joins required for person-company queries
- Higher storage usage due to duplication
- Fast reads, slower writes when company data changes

**Example Document:**

```javascript
// Person document with embedded company
{
    "_id": "person-uuid",
    "fullName": "John Doe", 
    "age": 30,
    "company": {
        "_id": "company-uuid",
        "name": "Tech Corp",
        "domain": "@techcorp.com",
        // ... complete company data
    },
    // ... other person fields
}
```

### Model 3: Denormalized (Embedded Employees in Company)
**Collections:** `Company` only

**Structure:**
- **Company Collection:** Contains company data with complete employee objects embedded in array

**Characteristics:**

- Person data duplicated within company documents
- No joins required for company-employee queries
- Documents can become very large with many employees
- Efficient for company-centric operations

**Example Document:**

```javascript
// Company document with embedded employees
{
    "_id": "company-uuid",
    "name": "Tech Corp",
    "employees": [
        {
            "_id": "person-uuid1",
            "fullName": "John Doe",
            "age": 30,
            // ... complete person data
        },
        {
            "_id": "person-uuid2", 
            "fullName": "Jane Smith",
            "age": 25,
            // ... complete person data
        }
    ],
    // ... other company fields
}
```

## Performance Queries

All models execute the same four queries to enable performance comparison:

1. **Query 1:** For each person, retrieve full name and their company's name
2. **Query 2:** For each company, retrieve its name and the number of employees  
3. **Query 3:** For each person born before 1988, update their age to 30
4. **Query 4:** For each company, update its name to "Company"

### Tested Performance Characteristics

With 100,000 documents created for each model and a ratio of 50:1 for person:company documents:

| Model   | Query 1             | Query 2              | Query 3             | Query 4              |
| ------- | ------------------- | -------------------- | ------------------- | -------------------- |
| Model 1 | 0.9943206310272217  | 0.006774187088012695 | 0.27086544036865234 | 0.023867368698120117 |
| Model 2 | 0.15731549263000488 | 0.038277387619018555 | 0.2630436420440674  | 0.6295936107635498   |
| Model 3 | 0.12442302703857422 | 0.011976003646850586 | 0.05445599555969238 | 0.04669666290283203  |

## File Structure

```
lab_2_BDM/
├── README.md
├── config.json
├── .env
├── model_query_program.py    # Main program
├── model1.py                 # Normalized model
├── model2.py                 # Denormalized (company in person)
├── model3.py                 # Denormalized (employees in company)
├── start_mongo.sh            # MongoDB startup script
├── stop_mongo.sh             # MongoDB shutdown script
├── mql_queries				  # Folder containing all of the Mongo Shell queries for each model
└── data/
    └── db/                   # MongoDB data directory
```

## Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running: `ps aux | grep mongod`
- Check if port 27017 is available: `netstat -an | grep 27017`
- Verify data directory permissions

### Python Issues
- Install missing packages: `pip install -r requirements.txt`
- Check Python version: `python --version`

### Performance Issues
- Start with smaller datasets (< 1000 documents) for initial testing
- Monitor system resources during large dataset generation