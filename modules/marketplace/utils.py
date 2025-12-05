# modules/marketplace/utils.py
import os, uuid, json
from pathlib import Path
import sqlite3
from datetime import datetime

BASE = Path.cwd()
UPLOADS = BASE / "uploads"
DB_PATH = BASE / "archirapid.db"
UPLOADS.mkdir(parents=True, exist_ok=True)

def save_upload(uploaded_file, prefix="file"):
    # uploaded_file: Streamlit UploadedFile or werkzeug FileStorage (for API)
    ext = Path(uploaded_file.name).suffix if hasattr(uploaded_file, "name") else ".bin"
    fname = f"{prefix}_{uuid.uuid4().hex}{ext}"
    dest = UPLOADS / fname
    # if streamlit file-like
    try:
        with open(dest, "wb") as f:
            f.write(uploaded_file.getbuffer())
    except Exception:
        # werkzeug or other
        uploaded_file.save(str(dest))
    return str(dest)

def db_conn():
    return sqlite3.connect(DB_PATH)

def insert_user(user):
    conn = db_conn(); c=conn.cursor()
    c.execute("INSERT INTO users (id,name,email,role,company,created_at) VALUES (?,?,?,?,?,?)",
              (user["id"], user["name"], user["email"], user["role"], user.get("company",""), datetime.utcnow().isoformat()))
    conn.commit(); conn.close()

def get_user_by_email(email):
    conn = db_conn(); c=conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    row = c.fetchone()
    conn.close()
    return row

def create_plot_record(plot):
    conn = db_conn(); c=conn.cursor()
    c.execute("""INSERT INTO plots (id,owner_id,title,cadastral_ref,surface_m2,buildable_m2,is_urban,vector_geojson,registry_note_path,photo_paths,price,lat,lon,status,owner_name,owner_phone,owner_address,sanitation,finca_type,created_at)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
              (plot["id"],plot["owner_id"],plot["title"],plot.get("cadastral_ref"),plot.get("surface_m2"),plot.get("buildable_m2"),1 if plot.get("is_urban") else 0,plot.get("vector_geojson"),plot.get("registry_note_path"),plot.get("photo_paths"),plot.get("price"),plot.get("lat"),plot.get("lon"),plot.get("status","published"),plot.get("owner_name"),plot.get("owner_phone"),plot.get("owner_address"),plot.get("sanitation"),plot.get("finca_type"),datetime.utcnow().isoformat()))
    conn.commit(); conn.close()

def list_published_plots():
    conn = db_conn(); c=conn.cursor()
    c.execute("SELECT id,title,cadastral_ref,surface_m2,buildable_m2,price,lat,lon,status FROM plots WHERE status='published'")
    rows = c.fetchall(); conn.close()
    cols = ["id","title","cadastral_ref","surface_m2","buildable_m2","price","lat","lon","status"]
    return [dict(zip(cols,r)) for r in rows]

def reserve_plot(plot_id, buyer_name, buyer_email, amount, kind="reservation"):
    conn = db_conn(); c=conn.cursor()
    rid = uuid.uuid4().hex
    c.execute("INSERT INTO reservations (id,plot_id,buyer_name,buyer_email,amount,kind,created_at) VALUES (?,?,?,?,?,?,?)",
              (rid, plot_id, buyer_name, buyer_email, amount, kind, datetime.utcnow().isoformat()))
    # set plot status
    if kind=="reservation":
        c.execute("UPDATE plots SET status='reserved' WHERE id=?", (plot_id,))
    elif kind=="purchase":
        c.execute("UPDATE plots SET status='sold' WHERE id=?", (plot_id,))
    conn.commit(); conn.close()
    return rid