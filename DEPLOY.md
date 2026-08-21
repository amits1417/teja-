# Deploy on Render or Railway (Flask + SQLite, no code changes needed)

## Render
1. Push this folder to a GitHub repo.
2. In Render: New → Web Service → connect repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Add environment variables (optional):
   - `TEJA_ADMIN_USER` / `TEJA_ADMIN_PASS` (change the default admin / teja123)
   - `TEJA_SECRET` (a random string)
   - `FLASK_DEBUG` = leave empty (production)
6. Deploy. Your site goes live at the given URL. Admin at `/admin`.

Note: on Render's free tier the disk is ephemeral (resets on each deploy),
so uploaded images / new products may not persist. To keep data, either:
 - upgrade to a paid instance with a persistent disk, or
 - move to Railway (persistent storage by default).

## Railway
1. Push to GitHub, then Railway: New Project → Deploy from GitHub repo.
2. Railway auto-detects Python; set the start command to `gunicorn app:app`
   (or it uses Procfile automatically).
3. Deploy. Admin at `/admin`.

## First steps after deploy
- Log in at `/admin` with admin / teja123 and change the password.
- Add your categories and products, upload images.
- Replace `static/images/logo.svg` with your real logo.
