import requests

BASE_URL = 'http://localhost:5000'  # Adjust if your server is running on a different port

def test_get_specific_job(job_id):
    url = f'{BASE_URL}/jobs/{job_id}'
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(f"Get Job {job_id} Response:", response.json())
    else:
        print(f"Error getting job {job_id}.")
        print("Response content:", response.text)

if __name__ == "__main__":
    # Hardcode the job ID here
    job_id = 5  # Change this to whatever ID you want to test
    test_get_specific_job(job_id)