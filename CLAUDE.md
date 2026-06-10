# CLAUDE.md — Finance Tracker

Handoff context for continuing work on this project in a new chat. Read this first.

## What this is

A personal finance tracker — a **Django 5** server-rendered web app (no SPA/REST API). Users log income/expenses, manage multiple accounts (bank, cash, wallet, savings, credit card), categorize spending, upload receipts, and view a dashboard + monthly reports. Single-developer hobby project, SQLite, runs locally.

- **Stack:** Django 5.0+, SQLite, Pillow (image handling). Frontend is Django templates + Bootstrap 5 + Bootstrap Icons + Chart.js (all via CDN, no build step / no npm).
- **Python:** 3.10+. Virtualenv lives in `venv/`.
- **Default currency:** NPR (रू). Per-user, configurable in profile.
- **Timezone:** Asia/Kathmandu. `USE_TZ = True`.

## Run / common commands

```bash
source venv/bin/activate
python manage.py runserver          # http://127.0.0.1:8000
python manage.py migrate
python manage.py makemigrations
python manage.py createsuperuser
python manage.py setup_demo_data    # demo user → demo / demo1234
python manage.py clean_orphaned_receipts
```

There is **no test suite** — every `apps/*/tests.py` is the empty Django stub. Don't claim tests pass; there are none to run.

## Project layout

Django settings module is `config.settings` (see [config/settings.py](config/settings.py)). Apps live under `apps/` and are namespaced (`apps.accounts`, etc.). All URL includes use `namespace=` so reverse names look like `wallets:detail`, `transactions:create`, `dashboard:index`.

| App | Purpose | Key models |
|-----|---------|-----------|
| `accounts` | Auth, user profile, currency, settings | `UserProfile` (OneToOne w/ User) |
| `wallets` | Accounts/wallets incl. **credit cards** | `Account`, `CreditCardPayment` |
| `transactions` | Income/expense records, receipts, quick-add templates | `Transaction`, `TransactionReceipt`, `TransactionTemplate` |
| `categories` | Spending categories (**shared across all users**) | `Category`, `SubCategory` |
| `dashboard` | Home view with computed financial overview | none (reads other apps) |
| `reports` | Per-month rollups with cached JSON breakdowns | `MonthlyReport` |

Templates: global ones in [templates/](templates/) (`base.html`, `components/`), app-specific under each `apps/<app>/templates/<app>/`. Static assets in [static/](static/), user uploads in [media/](media/) (`profiles/`, `receipts/`).

## Domain model — important details

These are the non-obvious rules that drive most bugs. Read before touching balances.

**`Account` ([apps/wallets/models.py](apps/wallets/models.py)) is the heart of the math.** Balances are computed properties (not stored), summed from `Transaction` rows each call:
- Transactions have `transaction_type` of `'credit'` (income/money in) or `'debit'` (expense/money out).
- **Regular account:** `current_balance = initial_balance + credits − debits`.
- **Credit card** (`account_type == 'credit'`): inverted — `current_balance = initial_balance + debits − credits`, i.e. positive = **debt owed**. Spending (debit) increases debt; payments (credit) reduce it. See `amount_owed`, `available_credit`, `credit_utilization`, `display_balance` (returns negative of debt), `actual_balance` (= available credit for cards).
- `savings_amount` is a per-account "set aside" carve-out. `actual_balance` (spendable) = `current_balance − savings_amount` for regular accounts.
- `include_in_total` toggles whether an account counts toward dashboard totals.
- Credit cards also carry `credit_limit`, `billing_due_date`, `minimum_payment`, and have due-status helpers (`days_until_due`, `is_overdue`, `due_status` → `overdue`/`due_soon`/`ok`/`no_due_date`).

**`CreditCardPayment`** auto-creates **two** `Transaction` rows in its `save()` (only on create): a `credit` on the card (reduces debt) and a `debit` on the source account (money out). It also snapshots `balance_before_payment` and can advance the card's `billing_due_date`. Don't double-count payments by also adding manual transactions.

**Dashboard totals** ([apps/dashboard/views.py](apps/dashboard/views.py)) deliberately **exclude credit cards** from `total_balance`/savings. `current_balance` shown = total regular balance − savings. Keep this exclusion in mind when changing totals.

**`Category`/`SubCategory` are global**, not per-user (`name` is unique, `created_by` is just metadata). Editing/deleting a category affects every user. `Transaction.category` is `SET_NULL` on delete.

**`MonthlyReport`** ([apps/reports/models.py](apps/reports/models.py)) caches per-month income/expense totals + category/income breakdowns as JSON. Regenerated on demand: `generate_for_month()`, `generate_all_for_user()`. The reports list view calls `generate_all_for_user` on every load, and all-time totals are recomputed from `Transaction` directly for accuracy. `unique_together = (user, year, month)`.

**`TransactionReceipt`** compresses/resizes uploads in `save()` via Pillow (max 1200px wide, target ≤250KB JPEG, drops quality stepwise). `.jpg` files are gitignored.

**`TransactionTemplate`** ("Quick Add") stores reusable transaction presets; `use_count` orders them most-used-first; `increment_use_count()` on use.

## Routes (namespaced)

- `/` → `dashboard:index`
- `/accounts/` → login, register, logout, profile, settings
- `/wallets/` → list, create, `<pk>/`, edit, delete, **`<pk>/pay/`** (cc_payment), **`<pk>/payment-history/`**
- `/transactions/` → list, create, bulk-import (CSV), detail, edit, delete; receipts upload/delete; quick-add (`quick-add/`, `/new/`, `/<pk>/use/`, edit, delete)
- `/categories/` → list/create/edit/delete + subcategory create/delete; JSON APIs: `api/subcategories/<category_id>/`, `api/search/`
- `/reports/` → monthly_list, `<pk>/` detail, `refresh/` (POST, JSON)
- `/admin/` → Django admin

Class-based views throughout (`ListView`/`CreateView`/`DetailView`/etc.), all gated by `LoginRequiredMixin`. The two category APIs return `JsonResponse` and are used for the dynamic transaction form.

## State of the repo (as of this handoff)

- Branch: `main`. Recent commits added credit-card payments and a savings-save bugfix; reports + new dashboard balance card landed earlier.
- **`PROJECT_STRUCTURE.md` and `README.md` are partially stale** — they predate the `reports` app, credit cards, `CreditCardPayment`, receipts, and quick-add templates. Trust the code (and this file) over them.
- **Untracked / not committed:** `backend/`, `.claude/`. `db.sqlite3` is gitignored (the working copy is dirty but ignored for commits).
- **`backend/` is a stray, unrelated PHP/Oracle snippet** (`db.php`, `test_query.php`) with **hardcoded DB credentials** — not part of the Django app and not wired into anything. Flag it; likely should be removed or moved out, and those credentials rotated. Don't treat it as project code.
- **Security note:** `config/settings.py` has `DEBUG = True` and a hardcoded `SECRET_KEY` — fine for local dev, must change before any real deployment. No production settings split exists yet.

## Conventions / gotchas when editing

- Server-rendered only — no JS framework, no API layer beyond the two category JSON endpoints. Add UI as Django templates extending `templates/base.html`.
- Money is `DecimalField(max_digits=12, decimal_places=2)`; keep using `Decimal`, not float, in Python math.
- Balances are **computed properties**, so they're always live but can be N+1 heavy on list pages — use `select_related`/aggregation when iterating accounts/transactions.
- A `post_save` signal on `User` auto-creates `UserProfile` ([apps/accounts/models.py](apps/accounts/models.py)); access `user.profile.currency_symbol` for display.
- Bootstrap message tags are remapped (`ERROR → danger`) in settings.
- Roadmap (per README, not yet built): budgets, recurring transactions, data export, dark mode, currency conversion, financial goals, email reports.
