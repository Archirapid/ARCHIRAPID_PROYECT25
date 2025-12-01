# modules/marketplace/api.py
import sys
sys.path.append('.')
from flask import Flask, request, jsonify, send_file
from modules.marketplace.utils import save_upload, create_plot_record, list_published_plots, reserve_plot
import uuid
app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status":"ok"})

@app.route("/api/upload-plot", methods=["POST"])
def api_upload_plot():
    # fields: owner_email, title, price, file (pdf)
    f = request.files.get("file")
    owner_email = request.form.get("owner_email")
    title = request.form.get("title","Parcela subida via API")
    price = float(request.form.get("price",0))
    lat = request.form.get("lat")
    lon = request.form.get("lon")
    if not f or not owner_email:
        return jsonify({"success":False,"error":"file and owner_email required"}),400
    path = save_upload(f, prefix="nota_api")
    # create minimal record
    plot = {
        "id": uuid.uuid4().hex,
        "owner_id": owner_email,
        "title": title,
        "cadastral_ref": None,
        "surface_m2": None,
        "buildable_m2": None,
        "is_urban": True,
        "vector_geojson": None,
        "registry_note_path": path,
        "price": price,
        "lat": float(lat) if lat else None,
        "lon": float(lon) if lon else None,
        "status":"published"
    }
    create_plot_record(plot)
    return jsonify({"success":True,"plot_id":plot["id"]})

@app.route("/api/plots")
def api_list_plots():
    return jsonify({"plots": list_published_plots()})

@app.route("/api/reserve", methods=["POST"])
def api_reserve():
    data = request.json
    plot_id = data.get("plot_id")
    buyer_name = data.get("buyer_name")
    buyer_email = data.get("buyer_email")
    amount = float(data.get("amount",0))
    kind = data.get("kind","reservation")
    rid = reserve_plot(plot_id,buyer_name,buyer_email,amount,kind)
    return jsonify({"success":True,"reservation_id":rid})

if __name__ == "__main__":
    app.run(port=5001, debug=True)