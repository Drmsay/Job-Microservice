# Import necessary libraries
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
import csv
import asyncio
from io import StringIO
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up database connection parameters
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

# Initialize Flask app and configure database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db = SQLAlchemy(app)

# Define JobEntry model
class JobEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100))
    description = db.Column(db.Text)
    posted_date = db.Column(db.Date)

    def to_dict(self):
        # Convert model instance to dictionary
        return {
            'id': self.id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'description': self.description,
            'posted_date': self.posted_date.isoformat() if self.posted_date else None
        }

# Asynchronous function to process CSV file
async def process_csv(file_content):
    csv_reader = csv.DictReader(StringIO(file_content))
    jobs = []
    for row in csv_reader:
        job = JobEntry(
            title=row['title'],
            company=row['company'],
            location=row.get('location', ''),
            description=row.get('description', ''),
            posted_date=datetime.strptime(row['posted_date'], '%Y-%m-%d').date() if row.get('posted_date') else None
        )
        jobs.append(job)
    return jobs

# Route for file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and file.filename.endswith('.csv'):
        file_content = file.read().decode('utf-8')
        
        # Process CSV file asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        jobs = loop.run_until_complete(process_csv(file_content))
        
        # Save jobs to database
        db.session.bulk_save_objects(jobs)
        db.session.commit()
        
        return jsonify({
            'message': 'File imported successfully.',
            'jobs_imported': len(jobs)
        }), 200
    else:
        return jsonify({'error': 'Invalid file format. Please upload a CSV file.'}), 400

# Route to get all jobs
@app.route('/jobs', methods=['GET'])
def get_jobs():
    jobs = JobEntry.query.all()
    return jsonify([job.to_dict() for job in jobs]), 200

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)