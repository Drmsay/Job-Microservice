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

2. Get all jobs:
  Endpoint: /jobs
  Method: GET
  Example using Python requests:

3. Get a specific job:

  Endpoint: /jobs/<job_id>
  Method: GET
  Example using Python requests:


4. Create a new job:

  Endpoint: /jobs
  Method: POST
  Content-Type: application/json
  Body: JSON object with job details
  Example using Python requests:
   

5. Update an existing job:

  Endpoint: /jobs/<job_id>
  Method: PUT
  Content-Type: application/json
  Body: JSON object with updated job details
  Example using Python requests:
 

6. Delete a job:

  Endpoint: /jobs/<job_id>
  Method: DELETE
  Example using Python requests:
 

How to Programmatically RECEIVE Data
  Data is received from the microservice in JSON format. Here's how to handle the responses:
  
  For successful requests, the response will have a status code of 200 (OK) or 201 (Created for POST requests).
  The response body will contain a JSON object or array, depending on the endpoint.

  Example of parsing the response:


For file upload (/upload endpoint):

  On success, you'll receive a JSON object with 'message' and 'total_rows' keys.
  On failure, you'll receive a JSON object with 'message', 'total_rows', 'error_count', and 'errors' keys.

  Example: 

