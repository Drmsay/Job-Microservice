# Job Import Microservice

This microservice provides functionality for importing job listings via CSV and retrieving job entries.

## Supported Operations

The microservice supports the following endpoints:

- Upload CSV file: `POST /upload`
- GET all jobs: `GET /jobs`

## How to programmatically REQUEST data from the microservice:

Example calls (Python):

```python
import requests

base_url = "http://localhost:5000"

# Upload a CSV file
files = {'file': open('jobs.csv', 'rb')}
response = requests.post(f"{base_url}/upload", files=files)

# GET all jobs
response = requests.get(f"{base_url}/jobs")
```

## How to programmatically RECEIVE data from the microservice:

The microservice returns data in JSON format. To receive and process the data:

```python
import requests

base_url = "http://localhost:5000"

# GET all jobs
try:
    response = requests.get(f"{base_url}/jobs")
    if response.status_code == 200:
        jobs = response.json()
        for job in jobs:
            print(f"Title: {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Location: {job['location']}")
            print(f"Description: {job['description']}")
            print(f"Posted Date: {job['posted_date']}")
            print("--------------------")  # Separator between jobs
    else:
        print(f"Error: {response.status_code}")
except requests.ConnectionError:
    print("Failed to connect to the server. Is it running?")
```

## Note on CSV Format

The CSV file for upload should have the following columns:
- title 
- company 
- location
- description
- posted_date (format: YYYY-MM-DD)

## Error Handling

The microservice will return appropriate HTTP status codes along with error messages in the response body for any issues encountered during requests.

