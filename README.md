# Personal Finance Tracker

A full-featured Django web application for personal finance tracking with a beautiful dashboard, transaction management, and insightful charts.

![Dashboard Preview](docs/dashboard.png)

## Features

- **Dashboard** - Overview of total balance, savings, and spending with interactive charts
- **Multi-Account Support** - Track Bank accounts, Digital wallets (eSewa, etc.), Cash, and Savings
- **Transaction Management** - Record income and expenses with categories
- **Categories & Subcategories** - Organize transactions with custom categories
- **Bulk Import** - Import transactions from CSV files
- **User Authentication** - Secure login with multi-user support
- **Responsive Design** - Works on desktop, tablet, and mobile
- **Charts & Visualization** - Income vs Expense charts, Category breakdowns

## Tech Stack

- **Backend**: Django 5.x
- **Database**: SQLite (development) / PostgreSQL (production)
- **Frontend**: HTML, CSS, JavaScript (no framework)
- **CSS Framework**: Bootstrap 5
- **Charts**: Chart.js
- **Icons**: Bootstrap Icons

## Quick Start

### 1. Clone the repository

```bash
git clone <repository-url>
cd finance_tracker
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (admin)

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

### 7. Open in browser

- **Main App**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/

## Default Admin Credentials (for testing)

- **Username**: admin
- **Password**: admin123

## Project Structure

```
finance_tracker/
├── apps/
│   ├── accounts/       # User authentication & profiles
│   ├── dashboard/      # Main dashboard & insights
│   ├── wallets/        # Bank accounts, wallets, cash
│   ├── transactions/   # Income/expense records
│   └── categories/     # Spending categories
├── config/             # Project settings
├── static/             # CSS, JS, images
├── templates/          # Global templates
└── media/              # User uploads
```

## Key URLs

| URL | Description |
|-----|-------------|
| `/` | Dashboard |
| `/accounts/login/` | Login |
| `/accounts/register/` | Register |
| `/accounts/profile/` | User profile |
| `/wallets/` | Manage accounts |
| `/transactions/` | View/add transactions |
| `/categories/` | Manage categories |

## CSV Import Format

To bulk import transactions, create a CSV with these columns:

```csv
date,description,amount,type,account,category,notes
2024-01-15,Grocery Shopping,3000,debit,Cash,Food,Weekly groceries
2024-01-14,Salary,50000,credit,Bank,Income,Monthly salary
```

## Customization

### Currency
Users can set their preferred currency in Profile Settings. Supported currencies:
- NPR (Nepali Rupee)
- USD, EUR, GBP
- INR, AUD, CAD
- JPY, CNY

### Categories
Default category icons and colors can be customized when creating categories.

## Production Deployment

1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Set up PostgreSQL database
4. Configure static files with `collectstatic`
5. Use gunicorn or uwsgi as WSGI server
6. Set up nginx as reverse proxy

## License

MIT License

## Contributing

Pull requests are welcome!
