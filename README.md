Zavi Luxe

Zavi Luxe is a full-stack fashion e-commerce web app built with Django. It covers the full shopping flow — browsing, cart, checkout with OTP-verified orders, order tracking/returns, wishlists, and reviews — backed by a Django admin dashboard for managing the catalog and orders.

Features

Storefront


Home, shop, category, and product detail pages
Product search
Product cards with discount pricing, sizes, stock, and "featured / new arrival / bestseller" tags


Cart & Checkout


Session-based cart for guests, persisted cart for logged-in users
Add / update / remove cart items with size selection
OTP email verification before an order is placed
Free shipping over ₹2999, flat ₹99 shipping otherwise
Order confirmation emails


Accounts


Register / login with OTP verification
A custom dual-auth middleware keeps the storefront session and the Django admin session independent, so an admin login/logout doesn't sign out shoppers (and vice versa)
Profile page


Orders


Order history with status tracking (pending → confirmed → processing → shipped → delivered)
Cancel an order before delivery
Request a return within 7 days of delivery


Other


Wishlist
Product reviews & ratings
Newsletter subscription
Static info pages: About, Contact, Shipping, Size Guide, Returns & Exchange


Admin


Manage categories, products, orders (with inline order items), carts, wishlists, and reviews from the Django admin


Tech Stack


Backend: Django (Python)
Database: SQLite
Frontend: Django templates, vanilla CSS/JS
Email: Django SMTP email backend (Gmail) for OTPs and order confirmations


Project Structure

zaviluxe/
├── manage.py
├── db.sqlite3
├── media/                 # uploaded category & product images
├── screenshots/            # app screenshots
├── zaviluxe/                # project settings, root urls, wsgi
└── store/                   # main app
    ├── models.py            # Category, Product, Cart, Order, Wishlist, Review, Subscriber ...
    ├── views.py              # storefront, cart, checkout, auth, orders logic
    ├── urls.py
    ├── middleware.py         # DualAuthMiddleware (separate shopper/admin sessions)
    ├── auth_utils.py         # frontend login/logout helpers
    ├── context_processors.py # cart item count in navbar
    ├── admin.py
    ├── static/store/         # css, js, images
    └── templates/store/      # html templates

Getting Started

Prerequisites


Python 3.10+
pip


Installation

bash# Clone the repo
git clone <your-repo-url>
cd zaviluxe

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install django

# Apply migrations
python manage.py migrate

# Create an admin user
python manage.py createsuperuser

# Run the dev server
python manage.py runserver

Visit http://127.0.0.1:8000/ for the storefront and http://127.0.0.1:8000/admin/ for the admin dashboard.

Environment configuration

zaviluxe/settings.py currently has DEBUG = True, a placeholder SECRET_KEY, and Gmail SMTP credentials hardcoded in the file so OTP and order emails can be sent. Before pushing this repo anywhere public or deploying it:


Rotate the Gmail app password that's currently in settings.py — treat it as compromised the moment it's committed.
Move all secrets out of settings.py into environment variables, e.g.:


python   import os
   SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
   EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
   EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')

and load them via a .env file (e.g. with python-decouple or django-environ), adding .env to .gitignore.
3. Set DEBUG = False and configure ALLOWED_HOSTS for production.

Screenshots

See the screenshots/ folder for UI previews.
