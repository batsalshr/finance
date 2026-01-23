# Personal Finance Tracker - Project Structure

```
finance_tracker/
│
├── manage.py
├── requirements.txt
├── .gitignore
│
├── config/                     # Project configuration
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   │
│   ├── accounts/               # User authentication & profiles
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py           # UserProfile (extends User)
│   │   ├── forms.py            # Registration, Login, Profile forms
│   │   ├── views.py            # Login, Register, Profile views
│   │   ├── urls.py
│   │   └── templates/
│   │       └── accounts/
│   │           ├── login.html
│   │           ├── register.html
│   │           └── profile.html
│   │
│   ├── dashboard/              # Main dashboard & insights
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── views.py            # Dashboard view with calculations
│   │   ├── urls.py
│   │   └── templates/
│   │       └── dashboard/
│   │           └── index.html
│   │
│   ├── wallets/                # Bank accounts, wallets, cash
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py           # Account model
│   │   ├── forms.py
│   │   ├── views.py            # CRUD for accounts
│   │   ├── urls.py
│   │   └── templates/
│   │       └── wallets/
│   │           ├── list.html
│   │           ├── detail.html
│   │           └── form.html
│   │
│   ├── transactions/           # Income & expense transactions
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── models.py           # Transaction model
│   │   ├── forms.py
│   │   ├── views.py            # CRUD + bulk import
│   │   ├── urls.py
│   │   └── templates/
│   │       └── transactions/
│   │           ├── list.html
│   │           ├── detail.html
│   │           ├── form.html
│   │           └── bulk_import.html
│   │
│   └── categories/             # Expense categories & subcategories
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py           # Category, SubCategory models
│       ├── forms.py
│       ├── views.py
│       ├── urls.py
│       └── templates/
│           └── categories/
│               ├── list.html
│               └── form.html
│
├── templates/                  # Global templates
│   ├── base.html               # Main layout with sidebar
│   ├── components/
│   │   ├── navbar.html
│   │   ├── sidebar.html
│   │   ├── messages.html
│   │   └── pagination.html
│   └── includes/
│       └── charts.html         # Chart.js templates
│
├── static/                     # Static files
│   ├── css/
│   │   ├── style.css           # Custom styles
│   │   └── dashboard.css
│   ├── js/
│   │   ├── main.js
│   │   └── charts.js           # Chart.js configurations
│   └── images/
│       └── default-avatar.png
│
└── media/                      # User uploads
    └── profiles/               # Profile pictures
```

---

## Apps Overview

| App | Purpose | Key Models |
|-----|---------|------------|
| `accounts` | User auth & profiles | `UserProfile` |
| `dashboard` | Main dashboard, insights | None (uses other models) |
| `wallets` | Bank/wallet/cash accounts | `Account` |
| `transactions` | Income/expense records | `Transaction` |
| `categories` | Spending categories | `Category`, `SubCategory` |

---

## Model Relationships

```
User (Django built-in)
  │
  ├── UserProfile (OneToOne)
  │     └── currency, profile_picture
  │
  ├── Account (ForeignKey) ──────────────┐
  │     └── name, type, initial_balance  │
  │                                      │
  ├── Category (ForeignKey)              │
  │     └── name, color, icon            │
  │           │                          │
  │           └── SubCategory (FK)       │
  │                 └── name             │
  │                                      │
  └── Transaction (ForeignKey) ──────────┘
        └── date, description, amount,
            type (credit/debit),
            account (FK), category (FK),
            subcategory (FK)
```

---

## Key Calculations (in Dashboard)

```python
# Total Balance = Sum of all account balances
total_balance = sum(account.current_balance for account in user_accounts)

# Total Savings = Sum of savings-type accounts only
total_savings = sum(account.current_balance for account in savings_accounts)

# Current Total = Total Balance - Total Savings
current_total = total_balance - total_savings

# Account Balance = Initial Balance + Credits - Debits
account_balance = initial_balance + total_credits - total_debits
```

---

## URL Structure

```
/                           → Dashboard
/accounts/login/            → Login
/accounts/register/         → Register
/accounts/logout/           → Logout
/accounts/profile/          → User profile

/wallets/                   → List accounts
/wallets/create/            → Create account
/wallets/<id>/              → Account detail
/wallets/<id>/edit/         → Edit account
/wallets/<id>/delete/       → Delete account

/transactions/              → List transactions
/transactions/create/       → Create transaction
/transactions/<id>/         → Transaction detail
/transactions/<id>/edit/    → Edit transaction
/transactions/<id>/delete/  → Delete transaction
/transactions/bulk-import/  → CSV bulk import

/categories/                → List categories
/categories/create/         → Create category
/categories/<id>/edit/      → Edit category
/categories/<id>/delete/    → Delete category
```

---

## Tech Stack

- **Backend:** Django 5.x
- **Database:** SQLite (development)
- **Frontend:** HTML, CSS, JavaScript
- **CSS Framework:** Bootstrap 5
- **Charts:** Chart.js
- **Icons:** Bootstrap Icons or Font Awesome
