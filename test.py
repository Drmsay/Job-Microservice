import requests
import os

# Base URL for the API
base_url = "http://localhost:5000"

# Function to print job details
def print_job_details(job):
    print(f"Job ID: {job.get('id', 'N/A')}")
    print(f"Title: {job.get('title', 'N/A')}")
    print(f"Company: {job.get('company', 'N/A')}")
    print(f"Location: {job.get('location', 'N/A')}")
    print(f"Description: {job.get('description', 'N/A')}")
    print(f"Posted Date: {job.get('posted_date', 'N/A')}")
    print("--------------------")

# Test CSV upload functionality
def test_upload_csv():
    print("Testing CSV upload:")
    csv_file_path = 'test_valid.csv'  # Path to the CSV file
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return

    # Send POST request to upload CSV
    with open(csv_file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(f"{base_url}/upload", files=files)

    # Process response
    if response.status_code == 200:
        result = response.json()
        print(f"Upload successful. {result.get('jobs_imported', 0)} jobs imported.")
    else:
        print(f"Error: Unable to upload CSV. Status code: {response.status_code}")
        print(f"Response: {response.text}")

# Test GET all jobs functionality
def test_get_jobs():
    print("\nFetching all jobs:")
    response = requests.get(f"{base_url}/jobs")

    # Process response
    if response.status_code == 200:
        jobs = response.json()
        if jobs:
            for job in jobs:
                print_job_details(job)
        else:
            print("No jobs found.")
    else:
        print(f"Error: Unable to fetch jobs. Status code: {response.status_code}")
        print(f"Response: {response.text}")

# Main execution
if __name__ == '__main__':
    test_upload_csv()
    test_get_jobs()