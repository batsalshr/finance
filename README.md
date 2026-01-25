# Finance Tracker

A modern, full-featured personal finance management application built with Django. Track your income, expenses, manage multiple accounts, and gain insights into your spending habits.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

### Dashboard
- **Financial Overview**: View total balance, monthly income, expenses, and savings at a glance
- **Interactive Charts**: Visualize income vs expenses over the last 6 months
- **Spending Breakdown**: See spending by category with horizontal bar charts
- **Quick Stats**: Track your financial health with real-time calculations

### Account Management
- **Multiple Accounts**: Manage bank accounts, cash, e-wallets, and more
- **Credit Cards**: Track credit limits, amount owed, and utilization percentage
- **Custom Icons & Colors**: Personalize each account for easy identification
- **Balance Tracking**: Automatic balance updates based on transactions

### Transactions
- **Quick Entry**: Streamlined form for fast transaction logging
- **Receipt Uploads**: Attach multiple photos/screenshots with automatic compression
- **Bulk Import**: Import transactions from CSV files
- **Smart Filtering**: Filter by date range, account, category, or search terms
- **Transaction Templates**: Create templates for recurring transactions (rent, subscriptions, etc.)

### Categories
- **Pre-built Categories**: Common categories included out of the box
- **Subcategories**: Organize with nested subcategories
- **Income & Expense Types**: Separate categories for different transaction types
- **Custom Icons & Colors**: Visual identification for each category

### Quick Add Templates
- **One-Click Transactions**: Save frequently used transaction details
- **Custom Templates**: Create templates with pre-filled description, account, category
- **Usage Tracking**: Most-used templates appear first
- **Visual Icons**: Assign icons and colors to templates

### User Settings
- **Profile Management**: Update name and profile picture
- **Currency Selection**: Choose from multiple currencies (NPR, USD, EUR, etc.)
- **Secure Authentication**: Login, registration, and password management

## Getting Started

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. **Clone or extract the project**
   ```bash
   cd finance_tracker
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # On macOS/Linux
   source venv/bin/activate
   
   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser** (optional, for admin access)
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

7. **Open your browser**
   Navigate to `http://127.0.0.1:8000`

### Demo Data (Optional)

To populate the app with sample data for testing:

```bash
python manage.py setup_demo_data
```

This creates a demo user with:
- **Username**: `demo`
- **Password**: `demo1234`
- Sample accounts, categories, and transactions

## Project Structure

```
finance_tracker/
├── apps/
│   ├── accounts/          # User authentication & profiles
│   ├── categories/        # Category & subcategory management
│   ├── dashboard/         # Main dashboard & analytics
│   ├── transactions/      # Transaction CRUD & templates
│   └── wallets/           # Account/wallet management
├── config/                # Django settings & URLs
├── media/                 # User uploads (receipts, profiles)
├── static/                # CSS, JS, images
├── templates/             # Base templates & components
├── manage.py
└── requirements.txt
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 5.0+ |
| Database | SQLite (default) |
| Frontend | HTML5, CSS3, JavaScript |
| CSS Framework | Bootstrap 5 |
| Icons | Bootstrap Icons |
| Charts | Chart.js |
| Image Processing | Pillow |

## Screenshots

### Dashboard
- Total balance overview
- Income vs Expenses chart
- Spending by category
- Recent transactions

### Transaction Form
- Compact, modern design
- Expense/Income toggle
- Collapsible notes & receipt sections
- Drag & drop receipt upload

### Accounts
- Regular accounts with balance
- Credit cards with utilization
- Visual icons and colors

## ⚙️ Configuration

### Database
By default, the app uses SQLite. To use PostgreSQL or MySQL, update `config/settings.py`:

```python
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

### Media Files
Uploaded receipts are stored in the `media/receipts/` directory. In production, configure proper media serving.

### Currency
Default currency is NPR (रू). Users can change their currency in Settings > Profile.

Available currencies:
- NPR (रू) - Nepalese Rupee
- USD ($) - US Dollar
- EUR (€) - Euro
- GBP (£) - British Pound
- INR (₹) - Indian Rupee
- And more...

## Security Features

- CSRF protection on all forms
- Password hashing with Django's default hasher
- User-specific data isolation
- Secure file upload handling
- Session-based authentication

## API Endpoints

The app includes internal API endpoints for dynamic functionality:

| Endpoint | Description |
|----------|-------------|
| `/categories/api/search/` | Search categories with autocomplete |
| `/categories/api/subcategories/<id>/` | Get subcategories for a category |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Roadmap

- [ ] Budget management & alerts
- [ ] Recurring transactions automation
- [ ] Data export (Excel, PDF reports)
- [ ] Dark mode
- [ ] Mobile app (React Native)
- [ ] Bank account sync (Plaid integration)
- [ ] Multi-currency support with conversion
- [ ] Financial goals tracking

## Known Issues

- Receipt compression may fail for very large images (>10MB)
- Chart.js animations may lag with large datasets

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Django](https://www.djangoproject.com/) - The web framework used
- [Bootstrap](https://getbootstrap.com/) - CSS framework
- [Chart.js](https://www.chartjs.org/) - JavaScript charting library
- [Bootstrap Icons](https://icons.getbootstrap.com/) - Icon library
- [Pillow](https://pillow.readthedocs.io/) - Image processing

---

<p align="center">
  Made with ❤️ for better financial management
</p>
