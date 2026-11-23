# Diamond Battery Service: website + admin panel

Flask (Python) website with a full admin panel. The owner manages **everything** on the site
(shop details, batteries, brands, services, warranty, FAQ, reviews, gallery, photos) from the browser.

## 1. Run on your computer
    pip install -r requirements.txt
    python app.py
Website: http://localhost:5000      Admin: http://localhost:5000/admin
First login: username `admin`, password `change-this-password` (from config.py).
**Change it immediately** in Admin > Login & password.

## 2. What the admin controls
Bookings (status, search, CSV) | Batteries catalogue (photo, model, capacity, warranty, price, brand, vehicles)
Brands (logo) | Vehicle categories (2 to 20 wheeler, home inverter) | Battery types | Services | Warranty cards
Car tips | FAQ | Customer reviews | Highlights (numbers) | Photo gallery | Shop settings (phones, address, hours, texts).
Every item can be added, edited, hidden, reordered or deleted. Changes show on the website immediately.

## 3. Placeholders
Empty fields show dashed placeholder boxes on the website. When the content is filled in,
untick "Show dashed placeholder boxes" in Admin > Shop settings.

## 4. Deploy (important: keep the data)
All data lives in two places: `site.db` (database) and `uploads/` (photos). They are created automatically
and must be kept safe. Back up both regularly.
- **PythonAnywhere / VPS (recommended):** files persist. Point WSGI to `from app import app as application`.
  With gunicorn: `gunicorn -w 2 -b 0.0.0.0:8000 app:app` behind Nginx with HTTPS.
- **Hosts that wipe files on restart (free Render/Heroku):** set env `DATA_DIR` to a persistent disk, or bookings, photos and edits will be lost.
- Set env `SECRET_KEY` (any long random text) in production. Use HTTPS so logins are encrypted.
- Optional env: `ADMIN_PASSWORD` (before the first run), `DATA_DIR`, `PORT`.

## 5. Security built in
Hashed password, session login, CSRF protection on every admin form, login rate limit,
booking-form spam limit and honeypot, image uploads validated and resized (JPG/PNG only).

## Files
app.py (routes) | models.py (data + image handling) | seed.py (starting content) | config.py (first-run login)
templates/ (website) | templates/admin/ (admin screens) | static/ (css, js, fonts)
