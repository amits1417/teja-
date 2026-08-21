"""
TEJA International - Packaging website with admin panel
Run: python app.py
Admin: /admin  (default login below)
"""
import os
import sqlite3
import secrets
from datetime import datetime
from flask import (
    Flask, request, render_template, redirect, url_for, session,
    flash, send_from_directory, abort
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "teja.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("TEJA_SECRET", secrets.token_hex(16))
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024  # 8 MB

# ---- Admin credentials (change these!) ----
ADMIN_USERNAME = os.environ.get("TEJA_ADMIN_USER", "admin")
ADMIN_PASSWORD_HASH = generate_password_hash(
    os.environ.get("TEJA_ADMIN_PASS", "teja123")
)

SITE = {
    "name": "PEKTRON PACKING SOLUTIONS",
    "contact_person": "SHREYAS",
    "phone": "+91 97279 33639",
    "phone_href": "919727933639",
    "email": "supreme.international1011@gmail.com",
    "tagline": "PREMIUM PACKAGING SOLUTIONS PROVIDER",
    "address": "195, Ground Floor Shantivan Society, Vibhag -1, Near Bhumi Park Society, Sarthana Jakatnaka, Surat - 395006",
    "footer_text": "By Supreme International",
}

DEFAULT_CATEGORIES = [
    {"name": "COSMETIC", "image": "cat_cosmetic.png",
     "desc": "Bottles, jars and closures for cosmetic and makeup packaging."},
    {"name": "SKINCARE", "image": "cat_skincare.png",
     "desc": "Jars, pumps and droppers for skincare and serum formulations."},
    {"name": "PERSONAL CARE", "image": "cat_personal.png",
     "desc": "Bottles, pumps and sticks for personal care products."},
    {"name": "CUSTOM OEM", "image": "cat_oem.png",
     "desc": "Custom moulded components and OEM packaging solutions."},
]

DEFAULT_PRODUCTS = {
    "COSMETIC": [
        ("Cosmetic Jar 30ml", "prod_cosmetic_1.png", "PET", "30 ml"),
        ("Cosmetic Bottle 100ml", "prod_cosmetic_2.png", "PET", "100 ml"),
        ("Lip Gloss Tube", "prod_cosmetic_3.png", "PP", "10 g"),
        ("Compact Case", "prod_cosmetic_4.png", "ABS", "15 g"),
    ],
    "SKINCARE": [
        ("Skincare Cream Jar", "prod_skincare_1.png", "PP", "50 g"),
        ("Serum Dropper Bottle", "prod_skincare_2.png", "Glass", "30 ml"),
        ("Lotion Pump Bottle", "prod_skincare_3.png", "PET", "200 ml"),
        ("Face Mask Pouch", "prod_skincare_4.png", "Laminate", "25 ml"),
    ],
    "PERSONAL CARE": [
        ("Shampoo Bottle", "prod_personal_1.png", "HDPE", "300 ml"),
        ("Body Wash Pump", "prod_personal_2.png", "PET", "500 ml"),
        ("Deodorant Stick", "prod_personal_3.png", "PP", "75 g"),
        ("Soap Box", "prod_personal_4.png", "PP", "100 g"),
    ],
    "CUSTOM OEM": [
        ("Custom Molded Jar", "prod_custom_1.png", "Custom", "Custom"),
        ("Custom Bottle", "prod_custom_2.png", "Custom", "Custom"),
        ("Custom Closure", "prod_custom_3.png", "Custom", "Custom"),
        ("OEM Component", "prod_custom_4.png", "Custom", "Custom"),
    ],
}


# ---------------- DB helpers ----------------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        image TEXT,
        description TEXT,
        position INTEGER DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER,
        name TEXT NOT NULL,
        slug TEXT UNIQUE NOT NULL,
        image TEXT,
        material TEXT,
        capacity TEXT,
        shape TEXT,
        application TEXT,
        description TEXT,
        position INTEGER DEFAULT 0,
        created_at TEXT,
        FOREIGN KEY(category_id) REFERENCES categories(id) ON DELETE SET NULL
    );
    """)
    conn.commit()
    conn.close()


def seed_defaults():
    conn = get_db()
    # Categories (with image + description)
    existing_cat = {row["name"] for row in conn.execute("SELECT name FROM categories").fetchall()}
    cat_ids = {}
    for i, c in enumerate(DEFAULT_CATEGORIES):
        if c["name"] not in existing_cat:
            conn.execute(
                "INSERT INTO categories (name, slug, image, description, position) "
                "VALUES (?,?,?,?,?)",
                (c["name"], slugify(c["name"]), c["image"], c["desc"], i),
            )
        else:
            conn.execute(
                "UPDATE categories SET image=?, description=? WHERE name=?",
                (c["image"], c["desc"], c["name"]),
            )
        row = conn.execute("SELECT id FROM categories WHERE name=?", (c["name"],)).fetchone()
        cat_ids[c["name"]] = row["id"]

    # Products (4 per category) — insert only if not already present
    existing_prod = {row["name"] for row in conn.execute("SELECT name FROM products").fetchall()}
    for cname, plist in DEFAULT_PRODUCTS.items():
        cid = cat_ids.get(cname)
        for j, (pname, img, material, cap) in enumerate(plist):
            if pname not in existing_prod:
                conn.execute(
                    "INSERT INTO products (category_id, name, slug, image, material, "
                    "capacity, description, position) VALUES (?,?,?,?,?,?,?,?)",
                    (cid, pname, slugify(pname + "-" + str(j)), img, material,
                     cap, pname + " — premium packaging solution by " + SITE["name"] + ".", j),
                )
                existing_prod.add(pname)
    conn.commit()
    conn.close()


def slugify(text):
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "item"


# ---------------- Public routes ----------------
@app.route("/")
def home():
    conn = get_db()
    cats = conn.execute("SELECT * FROM categories ORDER BY position, name").fetchall()
    featured = conn.execute(
        "SELECT p.*, c.name AS cat_name FROM products p "
        "LEFT JOIN categories c ON p.category_id=c.id "
        "ORDER BY p.position, p.id DESC LIMIT 8"
    ).fetchall()
    conn.close()
    return render_template("index.html", cats=cats, featured=featured, site=SITE)


@app.route("/about")
def about():
    return render_template("about.html", site=SITE)


@app.route("/products")
def products():
    conn = get_db()
    cats = conn.execute("SELECT * FROM categories ORDER BY position, name").fetchall()
    conn.close()
    return render_template("products.html", cats=cats, site=SITE)


@app.route("/category/<slug>")
def category(slug):
    conn = get_db()
    cat = conn.execute("SELECT * FROM categories WHERE slug=?", (slug,)).fetchone()
    if not cat:
        abort(404)
    items = conn.execute(
        "SELECT * FROM products WHERE category_id=? ORDER BY position, id DESC",
        (cat["id"],)
    ).fetchall()
    conn.close()
    return render_template("category.html", cat=cat, items=items, site=SITE)


@app.route("/product/<slug>")
def product_detail(slug):
    conn = get_db()
    p = conn.execute("SELECT * FROM products WHERE slug=?", (slug,)).fetchone()
    if not p:
        abort(404)
    conn.close()
    return render_template("product_detail.html", p=p, site=SITE)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        flash("Thank you! Your message has been recorded. We will contact you soon.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", site=SITE)


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


# ---------------- Admin ----------------
def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapper(*a, **k):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return f(*a, **k)
    return wrapper


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")
        if u == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, p):
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials.", "danger")
    return render_template("admin/login.html", site=SITE)


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    conn = get_db()
    cat_count = conn.execute("SELECT COUNT(*) c FROM categories").fetchone()["c"]
    prod_count = conn.execute("SELECT COUNT(*) c FROM products").fetchone()["c"]
    conn.close()
    return render_template("admin/dashboard.html", cat_count=cat_count,
                           prod_count=prod_count, site=SITE)


@app.route("/admin/categories", methods=["GET", "POST"])
@login_required
def admin_categories():
    conn = get_db()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "add":
            name = request.form.get("name")
            desc = request.form.get("description")
            image = save_image(request.files.get("image"))
            conn.execute(
                "INSERT INTO categories (name, slug, image, description, position) "
                "VALUES (?,?,?,?,?)",
                (name, slugify(name), image, desc,
                 int(request.form.get("position") or 0))
            )
            flash("Category added.", "success")
        elif action == "delete":
            conn.execute("DELETE FROM categories WHERE id=?",
                         (request.form.get("id"),))
            flash("Category deleted.", "success")
        conn.commit()
    cats = conn.execute("SELECT * FROM categories ORDER BY position, name").fetchall()
    conn.close()
    return render_template("admin/categories.html", cats=cats, site=SITE)


@app.route("/admin/category/edit/<int:cid>", methods=["GET", "POST"])
@login_required
def admin_category_edit(cid):
    conn = get_db()
    cat = conn.execute("SELECT * FROM categories WHERE id=?", (cid,)).fetchone()
    if not cat:
        abort(404)
    if request.method == "POST":
        image = save_image(request.files.get("image"), cat["image"])
        conn.execute(
            "UPDATE categories SET name=?, slug=?, description=?, image=?, position=? "
            "WHERE id=?",
            (request.form.get("name"), slugify(request.form.get("name")),
             request.form.get("description"), image,
             int(request.form.get("position") or 0), cid)
        )
        conn.commit()
        flash("Category updated.", "success")
        return redirect(url_for("admin_categories"))
    conn.close()
    return render_template("admin/category_edit.html", cat=cat, site=SITE)


@app.route("/admin/products", methods=["GET", "POST"])
@login_required
def admin_products():
    conn = get_db()
    if request.method == "POST":
        action = request.form.get("action")
        if action == "delete":
            conn.execute("DELETE FROM products WHERE id=?",
                         (request.form.get("id"),))
            flash("Product deleted.", "success")
            conn.commit()
    items = conn.execute(
        "SELECT p.*, c.name AS cat_name FROM products p "
        "LEFT JOIN categories c ON p.category_id=c.id ORDER BY p.position, p.id DESC"
    ).fetchall()
    conn.close()
    return render_template("admin/products.html", items=items, site=SITE)


@app.route("/admin/product/new", methods=["GET", "POST"])
@app.route("/admin/product/edit/<int:pid>", methods=["GET", "POST"])
@login_required
def admin_product_edit(pid=None):
    conn = get_db()
    cats = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
    prod = None
    if pid:
        prod = conn.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
        if not prod:
            abort(404)
    if request.method == "POST":
        name = request.form.get("name")
        data = (
            int(request.form.get("category_id") or 0) or None,
            name,
            slugify(name + "-" + secrets.token_hex(2)),
            save_image(request.files.get("image"), prod["image"] if prod else None),
            request.form.get("material"),
            request.form.get("capacity"),
            request.form.get("shape"),
            request.form.get("application"),
            request.form.get("description"),
            int(request.form.get("position") or 0),
        )
        if pid:
            conn.execute(
                "UPDATE products SET category_id=?, name=?, slug=?, image=?, "
                "material=?, capacity=?, shape=?, application=?, description=?, "
                "position=? WHERE id=?",
                data + (pid,)
            )
            flash("Product updated.", "success")
        else:
            conn.execute(
                "INSERT INTO products (category_id, name, slug, image, material, "
                "capacity, shape, application, description, position, created_at) "
                "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                data + (datetime.now().isoformat(),)
            )
            flash("Product added.", "success")
        conn.commit()
        conn.close()
        return redirect(url_for("admin_products"))
    conn.close()
    return render_template("admin/edit_product.html", prod=prod, cats=cats, site=SITE)


# ---------------- Image helper ----------------
ALLOWED = {"png", "jpg", "jpeg", "gif", "webp"}


def save_image(file, existing=None):
    if file and file.filename:
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext in ALLOWED:
            fn = secure_filename(f"{secrets.token_hex(8)}.{ext}")
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], fn))
            return fn
    return existing


init_db()
seed_defaults()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", host="0.0.0.0", port=port)
