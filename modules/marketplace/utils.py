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
    return fname  # devolver solo el nombre del archivo, no path completo

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
    from datetime import datetime
    from src import db

    data = {
        "id": plot.get("id"),
        "title": plot.get("title"),
        "description": plot.get("description", "") or plot.get("title"),
        "lat": plot.get("lat"),
        "lon": plot.get("lon"),
        "m2": plot.get("surface_m2") or plot.get("m2"),
        "height": plot.get("height") or plot.get("max_height") or None,
        "price": plot.get("price"),
        "type": plot.get("finca_type") or plot.get("type"),
        "province": plot.get("province"),
        "locality": plot.get("locality"),
        "owner_name": plot.get("owner_name") or plot.get("owner"),
        "owner_email": plot.get("owner_email"),
        "owner_phone": plot.get("owner_phone"),
        "image_path": None,
        "registry_note_path": plot.get("registry_note_path"),
        "address": plot.get("owner_address") or plot.get("address") or plot.get("plot_address"),
        "created_at": datetime.utcnow().isoformat(),
        "photo_paths": None,
    }

    # Normalize photo_paths and set image_path to first photo if available
    photo_paths = plot.get("photo_paths")
    if isinstance(photo_paths, list):
        data["photo_paths"] = ";".join(photo_paths)
        data["image_path"] = photo_paths[0] if len(photo_paths) > 0 else None
    elif isinstance(photo_paths, str):
        data["photo_paths"] = photo_paths
        parts = [p for p in photo_paths.split(";") if p.strip()]
        data["image_path"] = parts[0] if parts else (plot.get("image_path") or None)
    else:
        # fallback to any single image field present
        data["photo_paths"] = None
        data["image_path"] = plot.get("image_path") or plot.get("photo")

    # Ensure owner_email/name fallback from top-level plot fields if needed
    if not data["owner_email"]:
        data["owner_email"] = plot.get("email") or plot.get("owner_email_address")

    db.insert_plot(data)

def list_published_plots():
    conn = db_conn(); c=conn.cursor()
    c.execute("SELECT id,title,cadastral_ref,surface_m2,buildable_m2,price,lat,lon,status,photo_paths,registry_note_path FROM plots WHERE status='published'")
    rows = c.fetchall(); conn.close()
    cols = ["id","title","cadastral_ref","surface_m2","buildable_m2","price","lat","lon","status","photo_paths","registry_note_path"]
    return [dict(zip(cols,r)) for r in rows]

def list_projects():
    conn = db_conn(); c=conn.cursor()
    c.execute("""
        SELECT p.id, p.title, p.description, p.area_m2, p.price, p.files_json, p.characteristics_json, p.plot_id, p.created_at,
               u.name as architect_name, u.company
        FROM projects p
        LEFT JOIN users u ON p.architect_id = u.id
        ORDER BY p.created_at DESC
    """)
    rows = c.fetchall(); conn.close()
    cols = ["id","title","description","area_m2","price","files_json","characteristics_json","plot_id","created_at","architect_name","company"]
    projects = [dict(zip(cols,r)) for r in rows]
    for proj in projects:
        proj['files'] = json.loads(proj['files_json']) if proj['files_json'] else {}
        proj['characteristics'] = json.loads(proj['characteristics_json']) if proj['characteristics_json'] else {}
    return projects

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

def get_client_proposals(client_email):
    """Obtener propuestas recibidas por un cliente (owner) con JOIN completo"""
    conn = db_conn(); c = conn.cursor()
    c.execute("""
        SELECT 
            pr.id, pr.proposal_text, pr.estimated_budget, pr.deadline_days, pr.sketch_image_path, 
            pr.status, pr.created_at, pr.responded_at, pr.delivery_format, pr.delivery_price, 
            pr.supervision_fee, pr.visa_fee, pr.total_cliente, pr.commission, pr.project_id,
            pl.title as plot_title, pl.surface_m2 as plot_surface, pl.price as plot_price,
            ar.user_id as architect_user_id,
            u.name as architect_name, u.company as architect_company,
            pj.title as project_title, pj.description as project_description, pj.area_m2 as project_area, pj.price as project_price
        FROM proposals pr
        JOIN plots pl ON pr.plot_id = pl.id
        JOIN users u ON pr.architect_id = u.id  -- arquitecto user
        LEFT JOIN architects ar ON ar.user_id = pr.architect_id  -- architect details
        LEFT JOIN projects pj ON pr.project_id = pj.id
        WHERE pl.owner_id = (SELECT id FROM users WHERE email = ? AND role = 'owner')
        ORDER BY pr.created_at DESC
    """, (client_email,))
    rows = c.fetchall(); conn.close()
    cols = ["id", "proposal_text", "estimated_budget", "deadline_days", "sketch_image_path", 
            "status", "created_at", "responded_at", "delivery_format", "delivery_price", 
            "supervision_fee", "visa_fee", "total_cliente", "commission", "project_id",
            "plot_title", "plot_surface", "plot_price",
            "architect_user_id", "architect_name", "architect_company",
            "project_title", "project_description", "project_area", "project_price"]
    return [dict(zip(cols, r)) for r in rows]

def calculate_edificability(plot_surface_m2, percentage=0.33):
    """Calcular área edificable máxima basada en superficie de la finca y porcentaje (default 33%)"""
    return plot_surface_m2 * percentage

def update_proposal_status(proposal_id, status):
    """Actualizar status y responded_at de una propuesta"""
    from datetime import datetime
    conn = db_conn(); c = conn.cursor()
    c.execute("UPDATE proposals SET status = ?, responded_at = ? WHERE id = ?", 
              (status, datetime.utcnow().isoformat(), proposal_id))
    conn.commit(); conn.close()