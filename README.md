# TEJA International - Website + Admin Panel

A self-editable packaging company website (Flask + SQLite). Manage product
categories and products (add / edit / delete / image upload) from a password-
protected admin panel. No external database or services required.

## Run it
```
pip install -r requirements.txt
python app.py
```
Then open http://127.0.0.1:5000

## Admin
- URL: http://127.0.0.1:5000/admin
- Default login: **admin** / **teja123**  (change in app.py)

## Editing content
- Categories: /admin/categories  (add, edit name/description, upload image, reorder)
- Products:   /admin/products    (add new, edit, delete, assign to category, upload picture)
- Contact phone/email/name: edit the `SITE` dict in app.py

## Replace the logo
Drop your real logo at `static/images/logo.svg` (or change the reference in
templates/base.html). The current file is a placeholder SVG.

## Notes
- Images upload to `static/uploads/`.
- Database is `teja.db` (auto-created on first run).
- For production, set `TEJA_SECRET`, `TEJA_ADMIN_USER`, `TEJA_ADMIN_PASS`
  environment variables and disable debug mode.
