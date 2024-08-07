import requests
import os
import csv
from datetime import datetime

# Base URL for the API
base_url = "http://localhost:5000"

# Function to print job details
def print_job_details(job):
    print(f"Job ID: {job['id']}")
    print(f"Title: {job['title']}")
    print(f"Company: {job['company']}")
    print(f"Location: {job['location']}")
    print(f"Description: {job['description']}")
    print(f"Posted Date: {job['posted_date']}")
    print("--------------------")

# Function to validate CSV content
def validate_csv(file_path):
    required_columns = ['title', 'company', 'location', 'description', 'posted_date']
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        if not all(column in csv_reader.fieldnames for column in required_columns):
            missing_columns = set(required_columns) - set(csv_reader.fieldnames)
            print(f"Error: CSV is missing required columns: {', '.join(missing_columns)}")
            return False
        for row_number, row in enumerate(csv_reader, start=2):
            if any(not row[column].strip() for column in required_columns):
                print(f"Error: Empty value found in row {row_number}")
                return False
            try:
                datetime.strptime(row['posted_date'], '%Y-%m-%d')
            except ValueError:
                print(f"Error: Invalid date format in row {row_number}. Expected format: YYYY-MM-DD")
                return False
    return True

# Test CSV upload functionality
def test_upload_csv():
    print("Testing CSV upload:")
    csv_file_path = 'test_invalid.csv'  # Path to the CSV file
    if not os.path.exists(csv_file_path):
        print(f"Error: CSV file not found at {csv_file_path}")
        return

    if not validate_csv(csv_file_path):
        print("Error: CSV file is not valid")
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