# Finance Tracker

A personal finance management application built with Django. Track income, expenses, manage multiple accounts, and gain insights into your spending habits.

## Features

### Dashboard
- Financial overview with total balance, monthly income, expenses, and savings
- Income vs expenses chart (last 6 months)
- Spending breakdown by category

### Accounts
- Multiple account types (bank, cash, e-wallet)
- Credit card tracking with limits and utilization
- Custom icons and colors

### Transactions
- Quick entry form with receipt uploads
- Bulk import from CSV
- Filtering by date, account, category, or search
- Transaction templates for recurring entries

### Categories
- Pre-built categories included
- Subcategory support
- Separate income and expense types
- Custom icons and colors

### Quick Add Templates
- Save frequently used transaction details
- One-click transaction creation
- Usage tracking (most-used first)

## Installation

### Prerequisites
- Python 3.10+
- pip

### Setup

```bash
# Navigate to project
cd finance_tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

### Demo Data (Optional)

```bash
python manage.py setup_demo_data
```

Creates a demo user:
- Username: `demo`
- Password: `demo1234`

## Project Structure

```
finance_tracker/
├── apps/
│   ├── accounts/       # Authentication & profiles
│   ├── categories/     # Category management
│   ├── dashboard/      # Main dashboard
│   ├── transactions/   # Transaction CRUD
│   └── wallets/        # Account management
├── config/             # Django settings
├── media/              # User uploads
├── static/             # CSS, JS
├── templates/          # Base templates
└── requirements.txt
```

## Tech Stack

- **Backend:** Django 5.0+
- **Database:** SQLite (default)
- **Frontend:** HTML, CSS, JavaScript
- **Charts:** Chart.js
- **Icons:** Bootstrap Icons
- **Images:** Pillow

## Configuration

### Database

Default is SQLite. For PostgreSQL:

```python
# config/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'finance_tracker',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Currency

Default: NPR. Change in Settings > Profile.

Available: NPR, USD, EUR, GBP, INR, and more.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `/categories/api/search/` | Search categories |
| `/categories/api/subcategories/<id>/` | Get subcategories |

## Roadmap

- Budget management
- Recurring transactions
- Data export (Excel, PDF)
- Dark mode
- Multi-currency conversion
- Financial goals
- Email reports

## License

MIT License
