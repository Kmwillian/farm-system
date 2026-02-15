# 🌾 Farm Management System

A professional Django web application for managing dairy, livestock, crops, and farm finances. Optimized for mobile use.

## Features

- 🐄 **Dairy Management** - Track cows, sheep, milk production, health records
- 🌾 **Crop Management** - Manage farm plots, planting schedules, harvest tracking
- 💰 **Financial Management** - Income, expenses, profit/loss reports
- 📊 **Dashboard** - Real-time farm overview with alerts

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Admin User

```bash
python manage.py createsuperuser
```

### 4. Run Server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## Project Structure

```
FARM/
├── farm_project/         # Main Django project
├── dairy/               # Dairy & livestock app
├── crops/               # Crop management app
├── finance/             # Financial tracking app
├── dashboard/           # Main dashboard app
├── templates/           # HTML templates
├── static/             # CSS, JS, images
├── media/              # User uploads
├── manage.py           # Django management
└── requirements.txt    # Python dependencies
```

## Requirements

- Python 3.8+
- Django 5.0.1
- Pillow 10.2.0

## Deployment

See `DEPLOYMENT.md` for production deployment instructions.

## License

Custom system for farm management.