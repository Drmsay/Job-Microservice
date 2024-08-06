import requests
import json

BASE_URL = 'http://localhost:5000'

def test_upload_csv():
    url = f'{BASE_URL}/upload'
    files = {'file': ('test.csv', open('test.csv', 'rb'))}
    response = requests.post(url, files=files)
    result = response.json()
    print("Upload CSV Response:", json.dumps(result, indent=2))
    if 'errors' in result:
        print("Invalid entries found:")
        for error in result['errors']:
            print(f"  - {error}")

def test_get_jobs():
    url = f'{BASE_URL}/jobs'
    response = requests.get(url)
    if response.status_code == 200:
        jobs = response.json()
        print(f"Get Jobs Response: {len(jobs)} jobs found")
        print(json.dumps(jobs, indent=2))
        return jobs
    else:
        print(f"Error getting jobs. Status code: {response.status_code}")
        return None

def test_create_job():
    url = f'{BASE_URL}/jobs'
    new_job = {
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'location': 'Remote',
        'description': 'Exciting opportunity for a skilled developer',
        'posted_date': '2024-08-15'
    }
    response = requests.post(url, json=new_job)
    if response.status_code == 201:
        print("Create Job Response:", response.json())
        return response.json()['id']
    else:
        print(f"Error creating job. Status code: {response.status_code}")
        print("Response:", response.json())
        return None

def test_get_specific_job(job_id):
    url = f'{BASE_URL}/jobs/{job_id}'
    response = requests.get(url)
    if response.status_code == 200:
        print(f"Get Job {job_id} Response:", response.json())
    else:
        print(f"Error getting job {job_id}. Status code: {response.status_code}")

def test_update_job(job_id):
    url = f'{BASE_URL}/jobs/{job_id}'
    updated_data = {
        'title': 'Senior Software Engineer',
        'location': 'New York, NY'
    }
    response = requests.put(url, json=updated_data)
    if response.status_code == 200:
        print(f"Update Job {job_id} Response:", response.json())
    else:
        print(f"Error updating job {job_id}. Status code: {response.status_code}")
        print("Response:", response.json())

def test_delete_job(job_id):
    url = f'{BASE_URL}/jobs/{job_id}'
    response = requests.delete(url)
    if response.status_code == 204:
        print(f"Delete Job {job_id} Response: Successfully deleted")
    else:
        print(f"Error deleting job {job_id}. Status code: {response.status_code}")

def get_first_job_id(jobs):
    if jobs and len(jobs) > 0:
        return jobs[0]['id']
    return None

if __name__ == '__main__':
    print("Testing CSV Upload:")
    test_upload_csv()
    
    print("\nTesting Get All Jobs:")
    jobs = test_get_jobs()
    
    print("\nTesting Create New Job:")
    created_job_id = test_create_job()
    
    print("\nTesting Get All Jobs After Creation:")
    jobs = test_get_jobs()
    
    if jobs:
        job_id_to_test = get_first_job_id(jobs)
        if job_id_to_test is not None:
            print(f"\nTesting Get Specific Job (ID: {job_id_to_test}):")
            test_get_specific_job(job_id_to_test)
            
            print(f"\nTesting Update Job (ID: {job_id_to_test}):")
            test_update_job(job_id_to_test)
            
            print(f"\nTesting Get Updated Job (ID: {job_id_to_test}):")
            test_get_specific_job(job_id_to_test)
            
            print(f"\nTesting Delete Job (ID: {job_id_to_test}):")
            test_delete_job(job_id_to_test)
            
            print("\nTesting Get All Jobs After Deletion:")
            test_get_jobs()
        else:
            print("No jobs found to test individual job operations.")
    else:
        print("Unable to retrieve jobs for testing individual operations.")
    
    if created_job_id:
        print(f"\nCleaning up: Deleting created job (ID: {created_job_id})")
        test_delete_job(created_job_id)