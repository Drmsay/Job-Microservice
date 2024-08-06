# Job Import Microservice

This microservice allows for manual entry of job listings via CSV file upload, stores the data in a PostgreSQL database, and provides RESTful endpoints to retrieve and manage the imported job listings.

## Communication Contract

### How to Programmatically REQUEST Data

To request data from this microservice, you can use HTTP requests. Here are the available endpoints:

1. Upload CSV file:
   - Endpoint: `/upload`
   - Method: POST
   - Content-Type: multipart/form-data
   - Body: CSV file with key 'file'

   Example using Python requests:
   ```python
   import requests

   url = 'http://localhost:5000/upload'
   files = {'file': open('job_listings.csv', 'rb')}
   response = requests.post(url, files=files)
   print(response.json())

2. Get all jobs:
  Endpoint: /jobs
  Method: GET
  Example using Python requests:
    import requests
    
    url = 'http://localhost:5000/jobs'
    response = requests.get(url)
    print(response.json())

3. Get a specific job:

  Endpoint: /jobs/<job_id>
  Method: GET
  Example using Python requests:
    import requests

    job_id = 1
    url = f'http://localhost:5000/jobs/{job_id}'
    response = requests.get(url)
    print(response.json())

4. Create a new job:

  Endpoint: /jobs
  Method: POST
  Content-Type: application/json
  Body: JSON object with job details
  Example using Python requests:
    import requests

    url = 'http://localhost:5000/jobs'
    data = {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "San Francisco",
        "description": "Exciting opportunity for a skilled developer",
        "posted_date": "2024-08-15"
    }
    response = requests.post(url, json=data)
    print(response.json())

5. Update an existing job:

  Endpoint: /jobs/<job_id>
  Method: PUT
  Content-Type: application/json
  Body: JSON object with updated job details
  Example using Python requests:
    import requests

    job_id = 1
    url = f'http://localhost:5000/jobs/{job_id}'
    data = {
        "title": "Senior Software Engineer",
        "location": "Remote"
    }
    response = requests.put(url, json=data)
    print(response.json())

6. Delete a job:

  Endpoint: /jobs/<job_id>
  Method: DELETE
  Example using Python requests:
    import requests

    job_id = 1
    url = f'http://localhost:5000/jobs/{job_id}'
    response = requests.delete(url)
    print(response.status_code)

How to Programmatically RECEIVE Data
  Data is received from the microservice in JSON format. Here's how to handle the responses:
  
  For successful requests, the response will have a status code of 200 (OK) or 201 (Created for POST requests).
  The response body will contain a JSON object or array, depending on the endpoint.

  Example of parsing the response:
      import requests
      
      url = 'http://localhost:5000/jobs'
      response = requests.get(url)
      
      if response.status_code == 200:
          jobs = response.json()
          for job in jobs:
              print(f"Title: {job['title']}, Company: {job['company']}")
      else:
          print(f"Error: {response.status_code}")
          print(response.json())

For file upload (/upload endpoint):

  On success, you'll receive a JSON object with 'message' and 'total_rows' keys.
  On failure, you'll receive a JSON object with 'message', 'total_rows', 'error_count', and 'errors' keys.

  Example: 
    import requests
  
    url = 'http://localhost:5000/upload'
    files = {'file': open('job_listings.csv', 'rb')}
    response = requests.post(url, files=files)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result['message']}")
        print(f"Total rows imported: {result['total_rows']}")
    else:
        error = response.json()
        print(f"Error: {error['message']}")
        print(f"Total rows: {error['total_rows']}")
        print(f"Error count: {error['error_count']}")
        for err in error['errors']:
            print(err)
