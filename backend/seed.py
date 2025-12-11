import requests

API = "http://localhost:8000"

def seed_fincas():
    fincas = [
        {"direccion":"Calle Mayor 1, Madrid","superficie_m2":10500,"ref_catastral":"123-ABC","propietario_email":"prop1@mail.com","max_construible_m2":3500,"ubicacion_geo":{"lat":40.416,"lng":-3.703}},
        {"direccion":"Av. Diagonal 200, Barcelona","superficie_m2":8000,"ref_catastral":"456-DEF","propietario_email":"prop2@mail.com","max_construible_m2":2600,"ubicacion_geo":{"lat":41.385,"lng":2.173}},
        {"direccion":"Camino Real 5, Sevilla","superficie_m2":6000,"ref_catastral":"789-GHI","propietario_email":"prop3@mail.com","max_construible_m2":2000,"ubicacion_geo":{"lat":37.389,"lng":-5.984}}
    ]
    for f in fincas:
        r = requests.post(f"{API}/fincas", json=f)
        print("Finca creada:", r.json())

def seed_proyectos():
    proyectos = [
        {"finca_id":1,"nombre":"Proyecto Arquitecto A","autor_tipo":"arquitecto","version":1,"json_distribucion":{"program":{"rooms":[{"id":"r1","type":"bedroom","area":15},{"id":"r2","type":"bathroom","area":8}],"total_m2":23}},"total_m2":23,"precio_estimado":95000},
        {"finca_id":2,"nombre":"Proyecto Arquitecto B","autor_tipo":"arquitecto","version":1,"json_distribucion":{"program":{"rooms":[{"id":"r1","type":"living","area":30},{"id":"r2","type":"kitchen","area":12}],"total_m2":42}},"total_m2":42,"precio_estimado":120000}
    ]
    for p in proyectos:
        r = requests.post(f"{API}/proyectos", json=p)
        print("Proyecto creado:", r.json())

if __name__ == "__main__":
    seed_fincas()
    seed_proyectos()