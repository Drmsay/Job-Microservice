import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
import csv
import asyncio
from io import StringIO
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve database connection details from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Construct the database URL
db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Create the database if it doesn't exist
if not database_exists(db_url):
    create_database(db_url)

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Set maximum file size to 16MB

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define JobEntry model for database
class JobEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    posted_date = db.Column(db.Date, nullable=False)

    def to_dict(self):
        # Convert JobEntry object to dictionary for JSON serialization
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'posted_date': self.posted_date.isoformat()
        }

async def process_csv(file_content):
    # Create a CSV reader object
    csv_reader = csv.DictReader(StringIO(file_content))
    required_columns = ['title', 'company', 'location', 'description', 'posted_date']
    
    # Validate that all required columns are present in the CSV
    if not all(column in csv_reader.fieldnames for column in required_columns):
        missing_columns = set(required_columns) - set(csv_reader.fieldnames)
        raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
    
    jobs = []
    for row_number, row in enumerate(csv_reader, start=2):  # start=2 because row 1 is headers
        # Check for empty values in required fields
        if any(not row[column].strip() for column in required_columns):
            raise ValueError(f"Empty value found in row {row_number}: {row}")
        
        # Validate and parse the date
        try:
            posted_date = datetime.strptime(row['posted_date'], '%Y-%m-%d').date()
        except ValueError:
            raise ValueError(f"Invalid date format in row {row_number}: {row}. Expected format: YYYY-MM-DD")
        
        # Create JobEntry object and append to list
        job = JobEntry(
            title=row['title'],
            company=row['company'],
            location=row['location'],
            description=row['description'],
            posted_date=posted_date
        )
        jobs.append(job)
    return jobs

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if file is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Process the CSV file if it has the correct extension
    if file and file.filename.endswith('.csv'):
        try:
            file_content = file.read().decode('utf-8')
            
            # Set up and run asyncio event loop to process CSV
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            jobs = loop.run_until_complete(process_csv(file_content))
            
            # Bulk insert jobs into the database
            db.session.bulk_save_objects(jobs)
            db.session.commit()
            
            return jsonify({
                'message': 'File imported successfully.',
                'jobs_imported': len(jobs)
            }), 200
        except ValueError as e:
            # Handle validation errors
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            # Handle unexpected errors
            return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
    else:
        return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

@app.route('/jobs', methods=['GET'])
def get_jobs():
    # Retrieve all jobs from the database and return as JSON
    jobs = JobEntry.query.all()
    return jsonify([job.to_dict() for job in jobs]), 200

if __name__ == '__main__':
    # Create all database tables
    with app.app_context():
        db.create_all()
    # Run the Flask application in debug mode
    app.run(debug=True)