# Hostel Management System

## Prerequisites
- Python 3.x
- pip (Python package installer)

## Installation Steps

### 1. Create and Activate Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# For Windows
venv\Scripts\activate
# For macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies
```bash
# Install Django and other requirements
pip install -r requirements.txt
```

### 4. Database Setup
```
# Make migrations
python manage.py makemigrations account stock

# Apply migrations
python manage.py migrate
```

### 5. Create Admin User
```
python manage.py createsuperuser
```


### 6. Run Development Server
```
python manage.py runserver
```
Access the application at http://127.0.0.1:8000/
