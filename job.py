# Import necessary libraries
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
import csv
import asyncio
from concurrent.futures import ThreadPoolExecutor
from io import StringIO
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Construct database URL
db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create database if it doesn't exist
if not database_exists(db_url):
    create_database(db_url)

# Initialize Flask app and configure it
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Create a thread pool for concurrent processing
executor = ThreadPoolExecutor(max_workers=4)

# Define Job model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    posted_date = db.Column(db.Date)

    def to_dict(self):
        # Convert Job object to dictionary
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None
        }

def validate_job(row, row_number):
    # Validate a single job entry
    errors = []
    if not row.get('title'):
        errors.append(f"Row {row_number}: Title is required")
    if not row.get('company'):
        errors.append(f"Row {row_number}: Company is required")
    
    # Validate date format
    if 'posted_date' in row:
        try:
            datetime.strptime(row['posted_date'], '%Y-%m-%d')
        except ValueError:
            errors.append(f"Row {row_number}: Invalid date format for posted_date. Use YYYY-MM-DD")
    
    return errors

async def validate_chunk(chunk, start_row):
    # Validate a chunk of job entries
    errors = []
    for i, row in enumerate(chunk, start=start_row):
        errors.extend(validate_job(row, i))
    return errors

async def process_csv(file_content):
    # Process and validate CSV content
    csv_reader = csv.DictReader(StringIO(file_content))
    chunk_size = 1000
    chunks = []
    current_chunk = []
    total_rows = 0
    
    # Split CSV into chunks
    for row in csv_reader:
        current_chunk.append(row)
        total_rows += 1
        if len(current_chunk) == chunk_size:
            chunks.append(current_chunk)
            current_chunk = []
    
    if current_chunk:
        chunks.append(current_chunk)
    
    # Validate chunks concurrently
    validation_tasks = [validate_chunk(chunk, i*chunk_size+1) for i, chunk in enumerate(chunks)]
    validation_results = await asyncio.gather(*validation_tasks)
    
    all_errors = [error for chunk_result in validation_results for error in chunk_result]
    
    return all_errors, total_rows, chunks

def import_jobs(chunks):
    # Import job data into database
    for chunk in chunks:
        for row in chunk:
            job = Job(
                title=row['title'],
                company=row['company'],
                location=row.get('location', ''),
                description=row.get('description', ''),
                posted_date=datetime.strptime(row['posted_date'], '%Y-%m-%d').date() if row.get('posted_date') else None
            )
            db.session.add(job)
    db.session.commit()

@app.route('/upload', methods=['POST'])
def upload_file():
    # Handle CSV file upload
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.csv'):
        file_content = file.read().decode('utf-8')
        
        # Process CSV file
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        errors, total_rows, chunks = loop.run_until_complete(process_csv(file_content))
        
        if errors:
            return jsonify({
                'message': 'Validation failed. Data not imported.',
                'total_rows': total_rows,
                'error_count': len(errors),
                'errors': errors
            }), 400
        else:
            import_jobs(chunks)
            return jsonify({
                'message': 'File validated successfully. Data imported.',
                'total_rows': total_rows
            }), 200
    else:
        return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

@app.route('/jobs', methods=['GET'])
def get_jobs():
    # Retrieve all jobs
    jobs = Job.query.all()
    return jsonify([job.to_dict() for job in jobs]), 200

@app.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    # Retrieve a specific job
    job = Job.query.get_or_404(job_id)
    return jsonify(job.to_dict()), 200

@app.route('/jobs', methods=['POST'])
def create_job():
    # Create a new job
    data = request.json
    job = Job(
        title=data['title'],
        company=data['company'],
        location=data.get('location', ''),
        description=data.get('description', ''),
        posted_date=datetime.strptime(data['posted_date'], '%Y-%m-%d').date() if data.get('posted_date') else None
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict()), 201

@app.route('/jobs/<int:job_id>', methods=['PUT'])
def update_job(job_id):
    # Update an existing job
    job = Job.query.get_or_404(job_id)
    data = request.json
    job.title = data.get('title', job.title)
    job.company = data.get('company', job.company)
    job.location = data.get('location', job.location)
    job.description = data.get('description', job.description)
    if 'posted_date' in data:
        job.posted_date = datetime.strptime(data['posted_date'], '%Y-%m-%d').date()
    db.session.commit()
    return jsonify(job.to_dict()), 200

@app.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    # Delete a job
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    return '', 204

if __name__ == '__main__':
    # Create database tables and run the app
    with app.app_context():
        db.create_all()
    app.run(debug=True)