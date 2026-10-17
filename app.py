import os
import re
import sqlite3
from flask import Flask, request, jsonify, g
from flask_cors import CORS

app = Flask(__name__)
DATABASE = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "safeher.db"))
ALLOWED_ORIGINS = [x.strip() for x in os.environ.get("ALLOWED_ORIGINS", "*").split(",") if x.strip()]
CORS(app, resources={r"/api/*": {"origins": ALLOWED_ORIGINS}})

REGIONS = {"Adamaoua", "Centre", "Est", "Extrême-Nord", "Littoral", "Nord", "Nord-Ouest", "Ouest", "Sud", "Sud-Ouest"}
PROFILES = {"Personne intéressée", "Témoin / proche", "Professionnel(le) / association", "Autre"}

def connect_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    os.makedirs(os.path.dirname(DATABASE) or ".", exist_ok=True)
    db = sqlite3.connect(DATABASE)
    db.execute("""CREATE TABLE IF NOT EXISTS registrations (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      first_name TEXT NOT NULL, region TEXT NOT NULL, city TEXT NOT NULL,
      profile TEXT NOT NULL, phone TEXT, wants_followup INTEGER NOT NULL DEFAULT 0,
      consent INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""")
    db.commit()
    db.close()

@app.get("/")
def root():
    return jsonify({"app": "SAFEHER API", "status": "ok", "routes": ["/api/register", "/api/stats", "/health"]})

@app.get("/health")
def health():
    return jsonify({"status": "ok"})

@app.post("/api/register")
def register():
    data = request.get_json(silent=True) or {}
    # Honeypot: silently accept bot-like submissions without storing them.
    if str(data.get("website", "")).strip():
        return jsonify({"ok": True})
    first_name = str(data.get("first_name", "")).strip()
    region = str(data.get("region", "")).strip()
    city = str(data.get("city", "")).strip()
    profile = str(data.get("profile", "")).strip()
    phone = str(data.get("phone", "")).strip()
    consent = data.get("consent") is True
    wants_followup = data.get("wants_followup") is True
    if not first_name or len(first_name) > 70:
        return jsonify(error="Le prénom ou pseudonyme est obligatoire (70 caractères maximum)."), 400
    if region not in REGIONS:
        return jsonify(error="Choisissez une région valide."), 400
    if not city or len(city) > 90:
        return jsonify(error="La ville ou localité est obligatoire."), 400
    if profile not in PROFILES:
        return jsonify(error="Choisissez un profil valide."), 400
    if phone and not re.fullmatch(r"[+0-9 ()-]{6,22}", phone):
        return jsonify(error="Le numéro semble invalide. Vous pouvez laisser ce champ vide."), 400
    if not consent:
        return jsonify(error="Votre accord est nécessaire pour enregistrer l'inscription."), 400
    db = connect_db()
    db.execute("""INSERT INTO registrations
      (first_name, region, city, profile, phone, wants_followup, consent)
      VALUES (?, ?, ?, ?, ?, ?, 1)""",
      (first_name, region, city, profile, phone, int(wants_followup)))
    db.commit()
    return jsonify(ok=True, message="Inscription enregistrée."), 201

@app.get("/api/stats")
def stats():
    db = connect_db()
    total = db.execute("SELECT COUNT(*) n FROM registrations").fetchone()["n"]
    return jsonify(total=total)

init_db()
