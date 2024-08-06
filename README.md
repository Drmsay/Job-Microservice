# Job Management Microservice

This microservice provides functionality for managing job listings, including uploading job data via CSV, and performing CRUD operations on individual job entries.

## Communication Contract

1. How to programmatically REQUEST data from the microservice:

The microservice supports the following endpoints:

- GET all jobs: `GET /jobs`
- GET a specific job: `GET /jobs/<job_id>`
- Create a new job: `POST /jobs`
- Update a job: `PUT /jobs/<job_id>`
- Delete a job: `DELETE /jobs/<job_id>`
- Upload CSV file: `POST /upload`

Example calls (Python):

```python
import requests
import json

base_url = "http://localhost:5000"

# GET all jobs
response = requests.get(f"{base_url}/jobs")

# GET a specific job
job_id = 1
response = requests.get(f"{base_url}/jobs/{job_id}")

# POST a new job
new_job = {
    "title": "Software Engineer",
    "company": "Tech Co",
    "location": "Remote",
    "description": "Exciting opportunity for a skilled developer",
    "posted_date": "2023-06-01"
}
response = requests.post(f"{base_url}/jobs", json=new_job)

# PUT (update) a job
job_id = 1
updated_job = {
    "title": "Senior Software Engineer",
    "company": "Tech Co",
    "location": "New York",
    "description": "Leading role for an experienced developer",
    "posted_date": "2023-06-02"
}
response = requests.put(f"{base_url}/jobs/{job_id}", json=updated_job)

# DELETE a job
job_id = 1
response = requests.delete(f"{base_url}/jobs/{job_id}")

# Upload a CSV file
files = {'file': open('jobs.csv', 'rb')}
response = requests.post(f"{base_url}/upload", files=files)

How to programmatically RECEIVE data from the microservice:

The microservice returns data in JSON format. To receive and process the data:
import requests

base_url = "http://localhost:5000"

# GET all jobs
response = requests.get(f"{base_url}/jobs")

if response.status_code == 200:
    jobs = response.json()
    for job in jobs:
        print(f"Job ID: {job['id']}, Title: {job['title']}, Company: {job['company']}")
else:
    print(f"Error: {response.status_code}")

# GET a specific job
job_id = 1
response = requests.get(f"{base_url}/jobs/{job_id}")

if response.status_code == 200:
    job = response.json()
    print(f"Job ID: {job['id']}")
    print(f"Title: {job['title']}")
    print(f"Company: {job['company']}")
    print(f"Location: {job['location']}")
    print(f"Description: {job['description']}")
    print(f"Posted Date: {job['posted_date']}")
else:
    print(f"Error: {response.status_code}")

For POST and PUT requests, the response will include the created or updated job data in the same format as GET requests.
For DELETE requests, a successful operation returns a 204 No Content status.
For CSV uploads, the response will include a message about the success or failure of the upload, along with the total number of rows processed and any validation errors.
