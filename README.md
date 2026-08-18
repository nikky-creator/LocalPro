# LocalPro — Local Services Marketplace

LocalPro connects customers with local service providers — electricians, plumbers,
painters, cleaners, mechanics, tutors, carpenters, AC technicians, and more. Customers
search, filter, and book verified providers; providers manage a listing and respond to
booking requests; admins manage the whole marketplace from Django Admin.

Built with **Django 5 + Python**, SQLite, Bootstrap 5, and vanilla JS — no frontend
build step required. Bootstrap, Font Awesome, and all fonts are **self-hosted** in
`static/vendor/`, so the site works fully offline / on locked-down college networks
(no CDN dependency).

---

## Features

- **Authentication & roles** — separate Customer and Provider registration, login,
  logout, profile editing, role-based dashboards.
- **Search & discovery** — keyword search, category/city/rating/price filters, sorting,
  pagination.
- **Booking workflow** — Pending → Accepted / Rejected → Completed, or Cancelled by the
  customer. Providers accept/reject/complete from their dashboard or the booking detail
  page (with a rejection-reason modal).
- **Online payments (simulated)** — after a booking is completed, the customer pays via
  a card / UPI / net-banking checkout with a receipt and transaction ID. This is a
  self-contained demo gateway (see the note under "Payments" below) — no real charge is
  ever made, and no card data is ever stored.
- **Complaints / reports** — customers can report a provider on any responded-to booking
  (no-show, poor quality, overcharging, unprofessional behavior, property damage), and
  admins triage reports (Open → Under Review → Resolved/Dismissed) from Django Admin.
- **Reviews** — 1–5 stars + comment, one review per completed booking, dynamic average
  rating and a per-provider rating breakdown bar chart.
- **Multi-language UI** — English, Hindi (हिन्दी), Telugu (తెలుగు), and Tamil (தமிழ்),
  switchable from the navbar and remembered across visits.
- **Dark mode** — a navbar toggle switches the whole site between light and dark themes
  (persisted in the browser), built on Bootstrap 5.3's native dark-mode support.
- **Premium UI** — glassmorphism hero with an animated "service ring", dark-glass
  dashboards, scroll-reveal animations, toast notifications, custom 404/500 pages.
- **Django Admin** — fully customized admin for Users/Profiles, Categories, Providers,
  Bookings, Payments, Reports, Reviews, Testimonials, and Contact messages.
- **Sample data** — a management command seeds 8 categories, 16 providers, 8 customers,
  dozens of bookings across every status, plus payments, reports, and reviews.

---

## Payments — how it actually works

There's no real payment gateway wired in (that requires your own merchant account and
API keys, which nobody can generate on your behalf). Instead, `payments/` implements a
**complete, working, simulated checkout**:

- A real `Payment` model, checkout form (with card-number/expiry formatting, UPI ID
  validation), receipt page, and transaction IDs.
- Card/CVV fields are validated for realism but **never saved anywhere** — only the
  payment method, amount, and status are persisted. This mirrors real-world best
  practice: raw card data should never touch your own server.
- To go live with a real gateway later, replace the body of `payments.views.checkout`
  with a call to your provider's hosted checkout (Razorpay, Stripe, PayU, etc.) — the
  model, URLs, and receipt flow are already gateway-agnostic.

---

## Multi-language coverage

Navigation, footer, homepage, authentication, dashboards, and the booking/payment/
report flows are fully translated into Hindi, Telugu, and Tamil (149 translated
strings — see `locale/*/LC_MESSAGES/django.po`). Content that comes from the database
(category names, provider bios, testimonials) stays in whatever language it was entered
in, since translating user-generated content would need a separate content-translation
layer. Switch languages from the dropdown in the navbar.

To add more translated strings later: wrap new text in `{% trans "..." %}` (templates)
or `gettext_lazy()` (Python), then run:
```bat
python manage.py makemessages -l hi -l te -l ta
REM ...fill in the new msgstr lines in locale/<lang>/LC_MESSAGES/django.po...
python manage.py compilemessages
```
`compilemessages` needs the `gettext` package installed (on Windows, install it via
[gettext for Windows](https://mlocati.github.io/articles/gettext-iconv-windows.html) or
skip recompiling — the `.mo` files already shipped in this project work as-is).

---

## Tech Stack

| Layer      | Technology                                   |
|------------|-----------------------------------------------|
| Backend    | Django 5, Python 3                            |
| Database   | SQLite                                        |
| Frontend   | Bootstrap 5, vanilla JS, Font Awesome 6       |
| Fonts      | Space Grotesk, Inter, JetBrains Mono (self-hosted) |
| Auth       | Django's built-in authentication              |
| File uploads | Pillow (profile pictures, provider photos)  |

---

## Project Structure

```
LocalPro/
├── manage.py
├── requirements.txt
├── README.md
├── localpro/                  # project settings & root URLs
├── core/                      # home, about, contact, errors, seed_data command
├── accounts/                  # Profile model, registration, login, dashboards
├── services/                  # ServiceCategory & Provider models, search/listing
├── bookings/                  # Booking model & full booking workflow
├── reviews/                   # Review model & review submission
├── payments/                  # Payment model, simulated checkout & receipt
├── reports/                   # Report (complaint) model & moderation
├── locale/                    # hi / te / ta translations (.po + .mo)
├── templates/                 # all HTML templates (base + per-app + partials)
├── static/
│   ├── css/                   # base.css (design tokens + dark theme) + components.css
│   ├── js/                    # main.js (incl. dark-mode toggle)
│   ├── images/                # processed logo + favicon
│   └── vendor/                # self-hosted Bootstrap, Font Awesome, fonts
└── media/                     # uploaded profile pictures & provider photos
```

---

## Setup (Windows)

Open Command Prompt / PowerShell in the project folder and run:

```bat
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser
python manage.py runserver
```

Then open **http://127.0.0.1:8000/** in your browser.

> macOS/Linux: replace `venv\Scripts\activate` with `source venv/bin/activate`.

### What each command does
- `python manage.py migrate` — creates `db.sqlite3` and all tables.
- `python manage.py seed_data` — populates demo categories, providers, customers,
  bookings, and reviews (safe to re-run; pass `--flush` to wipe and reseed).
- `python manage.py createsuperuser` — creates your own admin login for `/admin/`.

---

## Demo Login Credentials

This project ships with a **pre-seeded `db.sqlite3`** so it works immediately after
`pip install` — no migrate/seed step required to see it fully populated. These accounts
already exist (password for all customer/provider accounts: `DemoPass123`):

| Role      | Usernames                  |
|-----------|-----------------------------|
| Customer  | `customer1` … `customer8`   |
| Provider  | `provider1` … `provider16`  |
| Admin     | `admin` / password `AdminPass123` (at `/admin/`) |

Or register your own account from the homepage ("Get Started"). Want a completely
fresh start instead? Delete `db.sqlite3` and run the setup commands below — the
`migrate` + `seed_data` + `createsuperuser` steps rebuild everything from scratch.

---

## Key URLs

| Page                     | URL                              |
|---------------------------|-----------------------------------|
| Home                      | `/`                                |
| Services (categories)     | `/services/`                       |
| Find Providers            | `/services/providers/`             |
| Provider Detail           | `/services/providers/<id>/`        |
| Register (choose role)    | `/accounts/register/`              |
| Login                     | `/accounts/login/`                 |
| Dashboard                 | `/accounts/dashboard/`             |
| Profile                   | `/accounts/profile/`               |
| Booking History           | `/bookings/history/`               |
| My Reports                | `/reports/my-reports/`             |
| Django Admin              | `/admin/`                          |

---

## Notes

- **DEBUG mode**: ships with `DEBUG = True` for easy local development. Set it to
  `False` and configure `ALLOWED_HOSTS` before any real deployment — the custom
  404/500 pages only render when `DEBUG = False`.
- **Secret key**: replace `SECRET_KEY` in `localpro/settings.py` before deploying.
- **File uploads**: profile pictures and provider photos are validated for type
  (JPG/PNG/WEBP) and size (max 5MB) both in the browser and on the server.
- **Timezone**: set to `Asia/Kolkata`; change `TIME_ZONE` in `settings.py` if needed.
